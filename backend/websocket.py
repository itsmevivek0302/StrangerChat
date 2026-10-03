from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.connections = defaultdict(set)

    async def connect(self, user_id: int, ws: WebSocket):
        self.connections[user_id].add(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        self.connections[user_id].discard(ws)
        if not self.connections[user_id]:
            self.connections.pop(user_id, None)
            return True
        return False

    async def send_user(self, user_id: int, data: dict):
        dead = []
        for ws in list(self.connections.get(user_id, set())):
            try:
                await ws.send_json(data)
            except (WebSocketDisconnect, RuntimeError, OSError):
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

manager = ConnectionManager()
