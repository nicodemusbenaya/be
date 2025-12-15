from pydantic import BaseModel
from typing import Optional

class JoinMatchmakingResponse(BaseModel):
    message: str
    room_id: Optional[int] = None
    leader_id: Optional[int] = None
