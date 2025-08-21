from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
import pandas as pd

# 라우터 임포트
from app.routers import client_handler
from app.routers import esp32_handler
from app.routers import log_handler

# FastAPI 인스턴스 생성
app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ YOLO 추론 및 WebSocket 핸들러 라우터 등록
app.include_router(client_handler.router)
app.include_router(esp32_handler.router)
app.include_router(log_handler.router)

# ✅ 정적 파일 mount (프론트엔드 html/css/js)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ✅ 루트 접속 시 index.html 반환
@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")
