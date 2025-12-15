from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from .model import Room

router = APIRouter(prefix="/rooms", tags=["Rooms"])


# GET /rooms - lihat semua room
@router.get("/")
def get_all_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()



# GET /rooms/my - lihat room user yang aktif
@router.get("/my")
def get_my_room(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    room = db.query(Room).filter(
        Room.leader_id == user.id
    ).first()

    if not room:
        return {"message": "Kamu belum ditempatkan dalam room."}

    return room
