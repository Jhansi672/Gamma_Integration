## Base Info

**API URL:** `http://your-server.com:8000` (replace with actual server)

**Try it yourself:** `http://your-server.com:8000/docs` (interactive playground)


## What you can do

There are basically 3 ways to generate presentations:

1. **Simple way** - Send request, wait 30-60 seconds, get link
2. **Better way** - Send request, get job ID, check status every few seconds
3. **Download** - Get the actual file

## The Endpoints

### 1. Generate Presentation (Simple)

**Call this:** `POST /api/generate-presentation`

**What to send:**
{
  "input_text": "Your topic here - be descriptive!",
  "export_as": "pdf",
  "num_cards": 5
}

Notes:
- `input_text` - This is the important part. More details = better presentation
- `export_as` - Either "pdf" or "pptx" (defaults to pdf if you don't specify)
- `num_cards` - How many slides you want (1 to 10, default is 5)

**What you get back:**

{
  "success": true,
  "data": {
    "generation_id": "abc123xyz",
    "file_name": "abc123xyz.pdf",
    "download_url": "/api/downloads/abc123xyz.pdf",
    "status": "completed"
  }
}


If something goes wrong:
{
  "success": false,
  "error": "Error message explaining what happened"
}
```

**Example code:**
```javascript
// In your React/Vue/whatever frontend
async function createPresentation(topic, details) {
  try {
    const response = await fetch('http://your-server.com:8000/api/generate-presentation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        input_text: `Title: ${topic}\n\nDetails:\n${details}`,
        export_as: 'pdf',
        num_cards: 5
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show download button with result.data.download_url
      console.log('Download here:', result.data.download_url);
    } else {
      // Show error message
      console.error('Oops:', result.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}
```

**Important:** This takes 30-60 seconds to complete. The user will have to wait. That's why async is better (see below).

---

### 2. Generate Presentation (Async - Recommended)

This is the better approach. Here's how it works:

**Step 1:** Start the generation

`POST /api/generate-presentation-async`

Send the same data as above. You'll get back:
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

**Step 2:** Check if it's ready

Keep calling: `GET /api/presentation-status/{job_id}` every 5 seconds

While it's working:
```json
{
  "status": "processing",
  "progress": 45,
  "download_url": null
}
```

When it's done:
```json
{
  "status": "completed",
  "progress": 100,
  "download_url": "/api/downloads/abc123.pdf"
}
```

**Full example:**
```javascript
async function createPresentationAsync(topic, details) {
  // Start generation
  const startResponse = await fetch('http://your-server.com:8000/api/generate-presentation-async', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input_text: `Title: ${topic}\n\n${details}`,
      export_as: 'pdf',
      num_cards: 5
    })
  });
  
  const { job_id } = await startResponse.json();
  
  // Check status every 5 seconds
  const checkInterval = setInterval(async () => {
    const statusResponse = await fetch(
      `http://your-server.com:8000/api/presentation-status/${job_id}`
    );
    const status = await statusResponse.json();
    
    // Update UI with progress
    updateProgressBar(status.progress);
    
    if (status.status === 'completed') {
      // Done! Show download button
      clearInterval(checkInterval);
      showDownloadButton(status.download_url);
      
    } else if (status.status === 'failed') {
      // Something went wrong
      clearInterval(checkInterval);
      showError(status.error);
    }
  }, 5000); // Every 5 seconds
}
```

---

### 3. Download the File

**Call this:** `GET /api/downloads/{file_name}`

Just use the download URL you got from the previous steps.

**Simplest way (HTML):**
```html
<a href="http://your-server.com:8000/api/downloads/abc123.pdf" download>
  Download Presentation
</a>
```

**Or download programmatically:**
```javascript
async function downloadFile(url) {
  const response = await fetch(url);
  const blob = await response.blob();
  
  // Create a temporary download link
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = 'presentation.pdf';
  a.click();
  
  // Clean up
  window.URL.revokeObjectURL(downloadUrl);
}
```

---

### 4. Health Check (Optional)

**Call this:** `GET /api/health`

Just checks if the API is alive. Returns:
```json
{
  "status": "healthy",
  "message": "Presentation API is running"
}
```

Useful for monitoring or debugging.

---

## Complete Integration Example

Here's everything put together in a React component:
```javascript
import React, { useState } from 'react';

function PresentationGenerator() {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [error, setError] = useState(null);
  
  const API_BASE = 'http://your-server.com:8000';

  const generatePresentation = async (topic, content) => {
    setLoading(true);
    setProgress(0);
    setError(null);
    setDownloadUrl(null);
    
    try {
      // Start generation
      const response = await fetch(`${API_BASE}/api/generate-presentation-async`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_text: `${topic}\n\n${content}`,
          export_as: 'pdf',
          num_cards: 5
        })
      });
      
      const { job_id } = await response.json();
      
      // Poll for completion
      const pollInterval = setInterval(async () => {
        const statusResponse = await fetch(
          `${API_BASE}/api/presentation-status/${job_id}`
        );
        const status = await statusResponse.json();
        
        setProgress(status.progress);
        
        if (status.status === 'completed') {
          clearInterval(pollInterval);
          setDownloadUrl(`${API_BASE}${status.download_url}`);
          setLoading(false);
        } else if (status.status === 'failed') {
          clearInterval(pollInterval);
          setError(status.error || 'Generation failed');
          setLoading(false);
        }
      }, 5000);
      
    } catch (err) {
      setError('Failed to generate presentation: ' + err.message);
      setLoading(false);
    }
  };

  return (
    <div className="presentation-generator">
      <button 
        onClick={() => generatePresentation('AI in Healthcare', 'Detailed content here')}
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Create Presentation'}
      </button>
      
      {loading && (
        <div className="progress">
          Creating your presentation... {progress}%
        </div>
      )}
      
      {error && (
        <div className="error">
          Error: {error}
        </div>
      )}
      
      {downloadUrl && (
        <a href={downloadUrl} download className="download-button">
          📥 Download Presentation
        </a>
      )}
    </div>
  );
}

export default PresentationGenerator;
```

---

## Things to Know

### Timing
- Generation takes 30-60 seconds on average
- Sometimes faster, sometimes slower depending on Gamma's load
- Timeout is set to 75 seconds max

### Input Guidelines
- `input_text` should be at least 10 characters
- More detail = better results
- Max 5000 characters (though you probably won't need that much)

### File Formats
- PDF works for everything
- PPTX is good if users want to edit the presentation later

### Error Handling
The API will return specific errors if something goes wrong:
- "Input text is too short" - Need more content
- "Gamma generation failed" - Issue with Gamma API
- "File not found" - Download link expired or file was deleted

Always handle these in your UI so users know what's happening.

---

## Testing

### Use the interactive docs
Go to `http://your-server.com:8000/docs` - you can test everything right in your browser. Super helpful for debugging.

### Quick test with curl
```bash
# Generate a presentation
curl -X POST http://localhost:8000/api/generate-presentation \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Top 5 pizza places in NYC", "export_as": "pdf", "num_cards": 5}'

# Check health
curl http://localhost:8000/api/health
```

---

## Common Issues

**"Connection refused"**
- Make sure the API is running (`uvicorn api:app --reload`)

**"CORS error"**
- Already configured to allow cross-origin requests
- If you're still getting errors, let me know your frontend URL

**"Generation takes too long"**
- Normal! Gamma sometimes takes 60+ seconds
- Use the async endpoint so users don't have to stare at a loading spinner


