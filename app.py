from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from utils import save_url_to_db, get_or_cache_short_url, track_clicks, get_clicks

app = FastAPI()


@app.post("/shorten/")
async def shorten_url(payload: dict):
    """Shorten a long url"""
    long_url = payload.get("long_url")
    if not long_url:
        raise HTTPException(status_code=400, detail="Long URL is required")

    short_url = await save_url_to_db(long_url)
    return JSONResponse(content={"short_url": short_url}, status_code=status.HTTP_201_CREATED)


@app.get("/{short_url}")
async def resolve_url(short_url: str):
    """Resolve a short URL to a long URL."""
    long_url = await get_or_cache_short_url(short_url)

    if not long_url:
        raise HTTPException(status_code=404, detail="URL not found")

    await track_clicks(short_url)
    return JSONResponse(content={"long_url": long_url}, status_code=status.HTTP_301_MOVED_PERMANENTLY)
