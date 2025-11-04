# Presentation Generator API

Hey! This is a simple API that generates presentations using Gamma AI. Built this to integrate with our Riaa chatbot.

## What does it do?

Basically, you send some text about what you want, and it creates a nice PDF or PowerPoint presentation for you. Takes about 30-60 seconds.

## Quick Start

### Installation
```bash
# Clone or download the project
cd your-project-folder

# Install dependencies
pip install -r requirements.txt

# Set up your API key
# Create a .env file and add:
GAMMA_API_KEY=your_gamma_api_key_here

# Run the server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be running at `http://localhost:8000`

### Test it out

Open your browser and go to:
```
http://localhost:8000/docs
```

You'll see a nice interface where you can test everything. Pretty cool!

## Files in this project

- `api.py` - Main API code (FastAPI)
- `gamma_service.py` - Handles the Gamma API calls
- `app.py` - Streamlit demo (optional, just for testing)
- `.env` - Your API keys (don't commit this!)
- `API_DOCS.md` - Detailed API documentation for the frontend team

## How it works

1. User sends text → API receives it
2. API calls Gamma to generate presentation
3. Gamma creates the presentation (takes ~30-60 seconds)
4. API downloads the file and saves it
5. User gets a download link
