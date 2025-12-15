# app/ws/router.py
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.ws.manager import manager, Connection
from app.db.database import get_db
from app.core.config import settings
from app.db import models

router = APIRouter(prefix="/ws", tags=["websocket"])

async def get_user_from_token(token: str, db: Session):
    """Decode JWT and load user."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise

    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise JWTError("user_id not in token")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise JWTError("user not found")
    return user


@router.websocket("/rooms/{room_id}")
async def websocket_room_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(None),
    db: Session = Depends(get_db)
):
    if not token:
        await websocket.close(code=4001)
        return

    # validate token
    try:
        user = await get_user_from_token(token, db)
    except Exception:
        await websocket.close(code=4002)
        return

    # Accept connection
    conn = Connection(
        websocket=websocket,
        user_id=user.id,
        username=(user.username or user.email or f"user{user.id}")
    )
    await manager.connect(room_id, conn)

    # Notify others
    await manager.broadcast(room_id, {
        "type": "user_join",
        "data": {"user_id": conn.user_id, "username": conn.username}
    })

    # Send initial user list
    users = await manager.list_users(room_id)
    await websocket.send_text(json.dumps({
        "type": "users_list",
        "data": users
    }))

    try:
        while True:
            raw = await websocket.receive_text()

            # Expect JSON
            try:
                payload = json.loads(raw)
            except:
                continue

            msg_type = payload.get("type")


            #            CHAT HANDLER
       
            if msg_type == "chat":
                text = payload.get("text", "")

                outgoing = {
                    "type": "chat",
                    "data": {
                        "user_id": conn.user_id,
                        "username": conn.username,
                        "text": text
                    }
                }

                await manager.broadcast(room_id, outgoing)

            # Unknown (optional handling)
            else:
                await manager.broadcast(room_id, {
                    "type": "unknown",
                    "data": payload
                })

    except WebSocketDisconnect:
        await manager.disconnect(room_id, conn)
        await manager.broadcast(room_id, {
            "type": "user_leave",
            "data": {"user_id": conn.user_id, "username": conn.username}
        })

    except Exception:
        await manager.disconnect(room_id, conn)
        await manager.broadcast(room_id, {
            "type": "user_leave",
            "data": {"user_id": conn.user_id, "username": conn.username}
        })
        try:
            await websocket.close()
        except:
            pass
