import httpx
from fastapi import HTTPException

async def fetch_jpeg(esp32_capture_url: str) -> bytes:
    """Fetch a JPEG frame from ESP32-CAM `/capture`.

    Why:
        The backend pulls a frame on demand (pull model) instead of keeping a
        device-originated stream. This keeps device code simple and reduces
        persistent connections on the server.

    Args:
        esp32_capture_url: Full URL to the ESP32 `/capture` endpoint.

    Returns:
        Raw JPEG bytes.

    Raises:
        HTTPException: 502 if the ESP32 request fails or returns a bad status.
    """
    try:
        timeout = httpx.Timeout(5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(esp32_capture_url)
            resp.raise_for_status()
            return resp.content
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"ESP32 request error: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"ESP32 HTTP {exc.response.status_code}: {exc}") from exc
