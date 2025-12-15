from sqlalchemy.orm import Session
from sqlalchemy import asc
from .model import Room

MAX_ROOM_CAPACITY = 4  # bebas kamu ubah

def find_or_create_room(db: Session, user_id: int):
    # 1. cari room yang belum penuh
    room = (
        db.query(Room)
        .filter(Room.current_count < Room.capacity)
        .order_by(asc(Room.id))
        .first()
    )

    # 2. Kalau tidak ada room → buat baru
    if not room:
        room = Room(
            leader_id=user_id,        # user pertama = leader
            capacity=MAX_ROOM_CAPACITY,
            current_count=0
        )
        db.add(room)
        db.commit()
        db.refresh(room)

    # 3. Tambahkan user ke dalam room
    room.current_count += 1

    # 4. Jika user merupakan orang pertama
    if room.current_count == 1:
        room.leader_id = user_id

    db.commit()
    db.refresh(room)

    return room
