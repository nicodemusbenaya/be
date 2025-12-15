# app/ws/manager.py
import asyncio
import json
from typing import Dict, List
from fastapi import WebSocket

class Connection:
    def __init__(self, websocket: WebSocket, user_id: int, username: str):
        self.websocket = websocket
        self.user_id = user_id
        self.username = username

class RoomConnectionManager:
    def __init__(self):
        # room_id -> list[Connection]
        self.rooms: Dict[int, List[Connection]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, room_id: int, conn: Connection):
        await conn.websocket.accept()
        async with self._lock:
            self.rooms.setdefault(room_id, []).append(conn)

    async def disconnect(self, room_id: int, conn: Connection):
        async with self._lock:
            conns = self.rooms.get(room_id, [])
            if conn in conns:
                conns.remove(conn)
            if not conns:
                # cleanup empty room
                self.rooms.pop(room_id, None)

    async def broadcast(self, room_id: int, message: dict):
        """send JSON message to all connections in room"""
        conns = list(self.rooms.get(room_id, []))
        if not conns:
            return
        text = json.dumps(message)
        for c in conns:
            try:
                await c.websocket.send_text(text)
            except Exception:
                # ignore individual send errors; disconnect will handle stale sockets
                pass

    async def list_users(self, room_id: int):
        return [{"user_id": c.user_id, "username": c.username} for c in self.rooms.get(room_id, [])]

# single global manager instance
manager = RoomConnectionManager()
