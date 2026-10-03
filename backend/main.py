import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, SessionLocal
from models import User, now as utc_now
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM
from websocket import manager
from routes import auth as auth_routes, users, chats, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="StrangerChat API", version="1.0.0")
allowed_origins = [
    origin.strip()
    for origin in os.getenv("STRANGERCHAT_CORS_ORIGINS", "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(users.router)
app.include_router(chats.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"name":"StrangerChat API","status":"running","docs":"/docs"}

@app.get("/health")
def health():
    return {"status":"ok"}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str):
    await ws.accept()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        await ws.close(code=1008)
        return

    db = SessionLocal()
    user = None
    connected = False
    try:
        user = db.get(User, uid)
        if not user:
            await ws.close(code=1008)
            return
        await manager.connect(uid, ws)
        connected = True
        user.is_online = True
        db.commit()
        await ws.send_json({"type":"connected","user_id":uid})
        while True:
            data = await ws.receive_json()
            if isinstance(data, dict) and data.get("type") == "typing":
                try:
                    target = int(data.get("to", 0))
                except (TypeError, ValueError):
                    continue
                if target > 0 and target != uid:
                    await manager.send_user(
                        target,
                        {"type":"typing","from":uid,"typing":bool(data.get("value"))},
                    )
    except WebSocketDisconnect:
        pass
    finally:
        try:
            if connected and manager.disconnect(uid, ws):
                user.is_online = False
                user.last_seen = utc_now()
                db.commit()
        finally:
            db.close()
