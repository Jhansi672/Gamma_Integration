import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GAMMA_API_KEY = os.getenv("GAMMA_API_KEY")
GAMMA_BASE_URL = os.getenv("GAMMA_BASE_URL", "https://gamma.app/api")

if not GAMMA_API_KEY:
    raise ValueError("❌ Missing GAMMA_API_KEY in .env file")

HEADERS = {
    "Authorization": f"Bearer {GAMMA_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Known valid Gamma API paths in different releases
GAMMA_ENDPOINTS = ["/content", "/documents", "/create"]


async def create_presentation(title: str, content: str) -> dict:
    """
    Creates a presentation via Gamma API.
    Automatically retries known endpoints until one works.
    """
    payload = {
        "title": title,
        "content": content
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        last_error = None
        for endpoint in GAMMA_ENDPOINTS:
            url = f"{GAMMA_BASE_URL}{endpoint}"
            try:
                response = await client.post(url, json=payload, headers=HEADERS)
                if response.status_code < 400:
                    return response.json()
                last_error = f"{response.status_code} - {response.text}"
            except Exception as e:
                last_error = str(e)

        return {
            "error": "All endpoints failed",
            "last_attempt": last_error,
            "hint": (
                "Try verifying which endpoint your Gamma key supports. "
                "Most users should use POST https://gamma.app/api/content."
            )
        }


async def get_presentation_status(presentation_id: str) -> dict:
    """
    Fetches a presentation's details.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{GAMMA_BASE_URL}/documents/{presentation_id}", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}",
                "message": e.response.text
            }
        except Exception as e:
            return {"error": "Unexpected error", "message": str(e)}
