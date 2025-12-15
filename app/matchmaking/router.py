from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from .service import join_matchmaking
from .schemas import JoinMatchmakingResponse
from app.db.models import Profile

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

@router.post("/join", response_model=JoinMatchmakingResponse)
def join_queue(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # ambil profile user
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="User belum membuat profile")

    result = join_matchmaking(
        db=db,
        user_id=current_user.id,
        role=profile.role
    )

    # result bisa {"message": "..."} atau hasil create_room
    return JoinMatchmakingResponse(
        message=result.get("message"),
        room_id=result.get("room_id"),
        leader_id=result.get("leader_id")
    )
