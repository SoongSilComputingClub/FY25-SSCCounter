from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="frontend")

LOG_PATH = Path("logs/count_log.csv")

@router.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request) -> HTMLResponse:
    """Render the logs page with count history.

    Why:
        Provide a quick human-readable view of recent counts for debugging
        and sanity checks without needing external tools.
    """
    if not LOG_PATH.exists():
        return templates.TemplateResponse("logs.html", {"request": request, "data": []})

    df = pd.read_csv(LOG_PATH)
    df = df.sort_values(by="timestamp", ascending=False)
    records = df.to_dict(orient="records")
    return templates.TemplateResponse("logs.html", {"request": request, "data": records})
