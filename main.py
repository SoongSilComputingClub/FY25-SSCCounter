import json
import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.esp32 import fetch_jpeg
from app.inference import load_model_once, detect_with_overlay
from app.log_handler import router as logs_router

# --- Config (.env) -----------------------------------------------------------

load_dotenv()

ESP32_URL = os.getenv("ESP32_URL", "")
MODEL_PATH = os.getenv("MODEL_PATH", "")
CONF_THRES = float(os.getenv("CONF_THRES", "0.5"))
IMG_SIZE = int(os.getenv("IMG_SIZE", "640"))

OVERLAY_SAVE = os.getenv("OVERLAY_SAVE", "1").lower() in ("1", "true", "yes")
OVERLAY_DIR = Path(os.getenv("OVERLAY_DIR", "logs/overlays"))

# --- App ---------------------------------------------------------------------

app = FastAPI(title="SSCCounter BE (WS client + ESP32 pull + overlay save)")

# Why: FE 개발 환경/배포 환경에서 출처가 달라도 접근 가능하도록 허용.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일은 /static 경로로만 제공(루트에 마운트하면 WS 핸드셰이크와 충돌 가능).
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def serve_index() -> FileResponse:
    """Serve the SPA entry (index.html)."""
    return FileResponse("frontend/index.html")

# 오버레이 이미지를 읽기 전용으로 노출.
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media/overlays", StaticFiles(directory=str(OVERLAY_DIR)), name="overlays")

# 로그 페이지 라우터 등록.
app.include_router(logs_router)

# 모델은 프로세스 시작 시 1회 로드하여 추론 지연을 줄임.
model = load_model_once(MODEL_PATH)

# CSV 로그 경로 준비.
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_CSV = LOG_DIR / "count_log.csv"

def append_log(count: int, source: str = "esp32", overlay_url: Optional[str] = None):
    header_needed = not LOG_CSV.exists()
    with LOG_CSV.open("a", encoding="utf-8") as f:
        if header_needed:
            f.write("timestamp,count,source,overlay_url\n")
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        ov = overlay_url or ""
        f.write(f"{ts},{count},{source},{ov}\n")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "esp32_url": ESP32_URL,
        "overlay_save": OVERLAY_SAVE,
        "overlay_dir": str(OVERLAY_DIR),
    }


# --- WebSocket for FE --------------------------------------------------------

@app.websocket("/v2/ws/client")
async def ws_client(websocket: WebSocket) -> None:
    """FE sends 'capture' → pull frame from ESP32 → infer → reply with count (+overlay)."""
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            if msg.strip().lower() != "capture":
                await websocket.send_text(json.dumps({"error": "unknown command"}))
                continue

            t0 = time.perf_counter()
            try:
                # 1) ESP32에서 프레임 가져오기
                jpeg = await fetch_jpeg(ESP32_URL)

                # 2) 단 한 번의 추론으로 카운트 + 오버레이 바이트 획득
                persons, _details, overlay_jpeg = detect_with_overlay(
                    model=model,
                    jpeg_bytes=jpeg,
                    conf_thres=CONF_THRES,
                    img_size=IMG_SIZE,
                )

                # 3) 필요 시 오버레이 저장
                overlay_url = None
                if OVERLAY_SAVE:
                    # 파일명: YYYYMMDD_HHMMSS_countX.jpg
                    stamp = time.strftime("%Y%m%d_%H%M%S")
                    fname = f"{stamp}_count{persons}.jpg"
                    fpath = OVERLAY_DIR / fname
                    fpath.write_bytes(overlay_jpeg)
                    overlay_url = f"/media/overlays/{fname}"

                # 4) 로그 적재
                append_log(persons, source="esp32", overlay_url=overlay_url)

                # 5) 응답
                elapsed = round(time.perf_counter() - t0, 3)
                resp = {"count": persons, "inference_time": elapsed}
                if overlay_url:
                    resp["overlay_url"] = overlay_url
                await websocket.send_text(json.dumps(resp))

            except Exception as e:
                await websocket.send_text(json.dumps({"error": f"{type(e).__name__}: {e}"}))

    except WebSocketDisconnect:
        # 정상 종료
        return
