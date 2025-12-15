from pydantic import BaseModel
from datetime import datetime

class RoomResponse(BaseModel):
    id: int
    leader_id: int | None
    status: str
    capacity: int
    current_count: int
    created_at: datetime

    class Config:
        orm_mode = True
