from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
import re
import uuid
from datetime import datetime

# Import your existing Gamma service
from gamma_service import create_presentation_from_text

# ==================== Initialize FastAPI ====================

app = FastAPI(
    title="Presentation Generation API",
    description="API for generating presentations using Gamma AI",
    version="1.0.0"
)

# Enable CORS (so frontend can call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Request/Response Models ====================

class PresentationRequest(BaseModel):
    """Request model for generating presentation"""
    input_text: str = Field(
        ..., 
        min_length=10,
        max_length=5000,
        description="The content/topic for the presentation"
    )
    export_as: str = Field(
        default="pdf",
        pattern="^(pdf|pptx)$",
        description="Export format: 'pdf' or 'pptx'"
    )
    num_cards: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of slides (1-10)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "input_text": "Top 5 Pizza Places in NYC with ratings and specialties",
                "export_as": "pdf",
                "num_cards": 5
            }
        }


class PresentationResponse(BaseModel):
    """Response model for successful generation"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class JobResponse(BaseModel):
    """Response model for async job"""
    success: bool
    job_id: str
    status: str
    status_url: Optional[str] = None


class JobStatusResponse(BaseModel):
    """Response model for job status check"""
    job_id: str
    status: str
    progress: int
    download_url: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str
    timestamp: str


# ==================== In-Memory Job Storage ====================
# In production, use Redis or a database

jobs_storage = {}


# ==================== ENDPOINT 1: Generate Presentation (Synchronous) ====================

@app.post("/api/generate-presentation", response_model=PresentationResponse)
def generate_presentation(request: PresentationRequest):
    """
    Generate a presentation synchronously (user waits 30-60 seconds)
    
    - **input_text**: The topic/content for the presentation
    - **export_as**: Format - 'pdf' or 'pptx' (default: 'pdf')
    - **num_cards**: Number of slides, 1-10 (default: 5)
    
    Returns download URL immediately after generation completes.
    """
    try:
        # Call your existing function
        result = create_presentation_from_text(
            input_text=request.input_text,
            export_as=request.export_as,
            num_cards=request.num_cards
        )
        
        # Check if generation failed
        if "error" in result:
            return PresentationResponse(
                success=False,
                error=result["error"]
            )
        
        # Extract file information
        file_name = result['file']
        generation_id = file_name.split('.')[0]
        
        # Create download URL
        download_url = f"/api/downloads/{file_name}"
        
        # Return success response
        return PresentationResponse(
            success=True,
            data={
                "generation_id": generation_id,
                "file_name": file_name,
                "download_url": download_url,
                "gamma_url": result.get('url'),  # Original Gamma URL
                "status": "completed",
                "created_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ==================== ENDPOINT 2: Download File ====================

@app.get("/api/downloads/{file_name}")
def download_file(file_name: str):
    """
    Download a generated presentation file
    
    - **file_name**: The name of the file (e.g., 'abc123.pdf')
    
    Returns the file for download.
    """
    try:
        # Security: Validate file name format
        if not re.match(r'^[a-zA-Z0-9_-]+\.(pdf|pptx)$', file_name):
            raise HTTPException(
                status_code=400,
                detail="Invalid file name format"
            )
        
        # Check if file exists
        if not os.path.exists(file_name):
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Determine MIME type
        if file_name.endswith('.pdf'):
            media_type = 'application/pdf'
        else:
            media_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        
        # Return file
        return FileResponse(
            path=file_name,
            media_type=media_type,
            filename=file_name,
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )


# ==================== ENDPOINT 3: Generate Presentation (Asynchronous) ====================

@app.post("/api/generate-presentation-async", response_model=JobResponse)
def generate_presentation_async(
    request: PresentationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a presentation asynchronously (returns immediately, user polls status)
    
    - **input_text**: The topic/content for the presentation
    - **export_as**: Format - 'pdf' or 'pptx' (default: 'pdf')
    - **num_cards**: Number of slides, 1-10 (default: 5)
    
    Returns job_id immediately. Use /api/presentation-status/{job_id} to check progress.
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Store initial job status
        jobs_storage[job_id] = {
            "status": "processing",
            "progress": 0,
            "download_url": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Start background task
        background_tasks.add_task(
            generate_in_background,
            job_id,
            request.input_text,
            request.export_as,
            request.num_cards
        )
        
        # Return immediately
        return JobResponse(
            success=True,
            job_id=job_id,
            status="processing",
            status_url=f"/api/presentation-status/{job_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start generation: {str(e)}"
        )


def generate_in_background(job_id: str, input_text: str, export_as: str, num_cards: int):
    """
    Background task for async generation
    """
    try:
        # Update progress: Started
        jobs_storage[job_id]["progress"] = 10
        jobs_storage[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Call Gamma API
        result = create_presentation_from_text(
            input_text=input_text,
            export_as=export_as,
            num_cards=num_cards
        )
        
        # Check if failed
        if "error" in result:
            jobs_storage[job_id].update({
                "status": "failed",
                "error": result["error"],
                "updated_at": datetime.now().isoformat()
            })
            return
        
        # Success! Update status
        file_name = result['file']
        download_url = f"/api/downloads/{file_name}"
        
        jobs_storage[job_id].update({
            "status": "completed",
            "progress": 100,
            "download_url": download_url,
            "file_name": file_name,
            "gamma_url": result.get('url'),
            "updated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        jobs_storage[job_id].update({
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.now().isoformat()
        })


# ==================== ENDPOINT 4: Check Job Status ====================

@app.get("/api/presentation-status/{job_id}", response_model=JobStatusResponse)
def check_job_status(job_id: str):
    """
    Check the status of an async presentation generation
    
    - **job_id**: The job ID returned from /api/generate-presentation-async
    
    Returns current status, progress, and download URL when ready.
    """
    # Check if job exists
    if job_id not in jobs_storage:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Get job data
    job_data = jobs_storage[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job_data["status"],
        progress=job_data["progress"],
        download_url=job_data.get("download_url"),
        error=job_data.get("error"),
        created_at=job_data["created_at"],
        updated_at=job_data["updated_at"]
    )


# ==================== ENDPOINT 5: Health Check ====================

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """
    Check if the API is running and healthy
    """
    return HealthResponse(
        status="healthy",
        message="Presentation API is running",
        timestamp=datetime.now().isoformat()
    )


# ==================== Root Endpoint ====================

@app.get("/")
def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Presentation Generation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate_sync": "/api/generate-presentation",
            "generate_async": "/api/generate-presentation-async",
            "check_status": "/api/presentation-status/{job_id}",
            "download": "/api/downloads/{file_name}",
            "health": "/api/health",
            "docs": "/docs"
        }
    }


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (disable in production)
    )