# app/ws/schemas.py
from pydantic import BaseModel

class WSIncomingMessage(BaseModel):
    type: str  # "message" | "typing" | ...
    content: str | None = None

class WSOutgoingMessage(BaseModel):
    type: str  # "message" | "user_join" | "user_leave" | "users_list"
    data: dict | list | str | None = None
