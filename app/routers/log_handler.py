from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import pandas as pd

router = APIRouter()
templates = Jinja2Templates(directory="frontend")

@router.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request):
    log_path = "logs/count_log.csv"
    if not os.path.exists(log_path):
        return templates.TemplateResponse("logs.html", {"request": request, "data": []})

    df = pd.read_csv(log_path)
    df = df.sort_values(by="timestamp", ascending=False)
    records = df.to_dict(orient="records")
    return templates.TemplateResponse("logs.html", {"request": request, "data": records})
