import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GAMMA_API_KEY = os.getenv("GAMMA_API_KEY")
BASE_URL = "https://public-api.gamma.app/v0.2"

if not GAMMA_API_KEY:
    raise ValueError("❌ Missing GAMMA_API_KEY in .env file")

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": GAMMA_API_KEY
}

def create_presentation_from_text(input_text: str, export_as="pdf", num_cards=5):
    """
    Create and download a presentation (PDF or PPTX) from Gamma API.
    """
    resp = requests.post(
        f"{BASE_URL}/generations",
        headers=HEADERS,
        json={
            "inputText": input_text,
            "textMode": "generate",
            "format": "presentation",
            "exportAs": export_as,
            "numCards": num_cards
        },
    )

    if resp.status_code >= 400:
        return {"error": f"Failed to start generation: {resp.text}"}

    generation_id = resp.json().get("generationId")
    if not generation_id:
        return {"error": "Missing generationId in response."}

    # Poll status
    for _ in range(15):
        time.sleep(5)
        res = requests.get(f"{BASE_URL}/generations/{generation_id}", headers=HEADERS)
        data = res.json()
        status = data.get("status")
        if status == "completed":
            export_url = data.get("exportUrl")
            file_data = requests.get(export_url).content
            file_name = f"{generation_id}.{export_as}"
            with open(file_name, "wb") as f:
                f.write(file_data)
            return {"status": "completed", "file": file_name, "url": export_url}
        elif status == "failed":
            return {"error": "Gamma generation failed."}

    return {"error": "Gamma generation timed out."}
