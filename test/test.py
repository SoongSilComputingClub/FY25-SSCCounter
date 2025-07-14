from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio

app = FastAPI()
esp32_socket = None  # ESP32 연결 소켓
viewer_clients = []  # 브라우저 시청자들

@app.websocket("/ws/esp32/stream")
async def video_feed(websocket: WebSocket):
    global esp32_socket
    esp32_socket = websocket
    await websocket.accept()
    print("📡 ESP32 Connected")
    try:
        while True:
            data = await websocket.receive_bytes()
            # 스트리밍 on일 때만 전송 (추가 구현 가능)
            for client in viewer_clients:
                try:
                    await client.send_bytes(data)
                except Exception:
                    pass
    except WebSocketDisconnect:
        print("❌ ESP32 Disconnected")
        esp32_socket = None

@app.websocket("/ws/video")
async def video_viewer(websocket: WebSocket):
    global esp32_socket
    await websocket.accept()
    print("👀 Viewer Connected")
    viewer_clients.append(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            # 웹에서 "start" / "stop" 명령을 받으면 ESP32에 전달
            if msg == "start" and esp32_socket:
                await esp32_socket.send_text("start")
            elif msg == "stop" and esp32_socket:
                await esp32_socket.send_text("stop")
            # ping 등 기타 무시
    except WebSocketDisconnect:
        print("👋 Viewer Disconnected")
        viewer_clients.remove(websocket)