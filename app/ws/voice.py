# from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# router = APIRouter()

# active_connections = []


# @router.websocket("/ws/voice")
# async def voice_ws(websocket: WebSocket):
#     await websocket.accept()
#     active_connections.append(websocket)

#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             # broadcast ke client lain
#             for conn in active_connections:
#                 if conn != websocket:
#                     await conn.send_bytes(data)

#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
