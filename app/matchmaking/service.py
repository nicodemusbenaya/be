from sqlalchemy.orm import Session
from fastapi import HTTPException
import random
from app.rooms.model import Room
from .models import RoomMember, RoomHistory
from .queue import add_to_queue, count_queue, get_all_queue, clear_queue
from app.db.models import Profile  # kalau file kamu beda, sesuaikan
from sqlalchemy.orm import Session
from fastapi import HTTPException
import random

from .queue import (
    add_to_queue,
    is_in_queue,
    get_all_queue,
    get_queue_by_role,
    remove_many_from_queue
)
from app.db.models import Profile

# roles required (normalized keys)
REQUIRED = {
    "pm": 1,
    "qa": 1,
    "be": 2,
    "fe": 2
}

# map possible role strings to normalized keys
ROLE_MAP = {
    "project manager": "pm",
    "project_manager": "pm",
    "pm": "pm",

    "quality assurance": "qa",
    "quality_assurance": "qa",
    "qa": "qa",
    "tester": "qa",
    "quality": "qa",

    "backend": "be",
    "back-end": "be",
    "be": "be",
    "backend dev": "be",
    "backend_dev": "be",

    "frontend": "fe",
    "front-end": "fe",
    "fe": "fe",
    "frontend dev": "fe",
    "frontend_dev": "fe",
}

def normalize_role(raw: str) -> str:
    if not raw:
        return raw
    r = raw.strip().lower().replace("-", " ").replace(".", " ")
    # try direct match first
    if r in ROLE_MAP:
        return ROLE_MAP[r]
    # try word contains
    for k in ROLE_MAP:
        if k in r:
            return ROLE_MAP[k]
    # fallback: if single word 'backend' etc
    token = r.split()[0]
    return ROLE_MAP.get(token, r)  # if can't map, return original (unsafe)

def join_matchmaking(db: Session, user_id: int, role: str):
    # 1. cek profile ada
    profile = db.query(Profile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="User belum membuat profile.")

    # normalize role from profile if role param not passed
    normalized = normalize_role(role or profile.role)

    # 2. cek sudah di queue?
    if is_in_queue(db, user_id):
        raise HTTPException(status_code=400, detail="User sudah berada dalam queue.")

    # 3. tambah ke queue
    add_to_queue(db, user_id, normalized)

    # 4. coba proses matchmaking
    created = try_process_match(db)
    if created:
        return created
    return {"message": "Joined matchmaking queue"}

def try_process_match(db: Session):
    """
    Check whole queue and create a room if we can satisfy REQUIRED composition.
    Returns created room info or None.
    """
    # read all queue entries
    queue_entries = get_all_queue(db)
    if not queue_entries:
        return None

    # group by role
    buckets: dict[str, list[int]] = {}
    for e in queue_entries:
        buckets.setdefault(e.role, []).append(e.user_id)

    # quick check: do we have enough for every required role?
    for needed_role, needed_count in REQUIRED.items():
        have = len(buckets.get(needed_role, []))
        if have < needed_count:
            return None  # not enough yet

    # pick users for each role (randomly)
    selected_user_ids: list[int] = []
    for needed_role, needed_count in REQUIRED.items():
        candidates = buckets.get(needed_role, [])
        chosen = random.sample(candidates, needed_count)
        selected_user_ids.extend(chosen)

    # create room (import Room model at runtime to avoid circular import)
    from app.db.database import SessionLocal  # not used, but ensure db utils available
    # import Room model from rooms module (assumes app.rooms.model.Room exists)
    try:
        from app.rooms.model import Room
    except Exception:
        # if user hasn't a separate rooms model, create table with extend_existing - but prefer app.rooms.model
        raise HTTPException(status_code=500, detail="Room model not found (expected app.rooms.model.Room).")

    # create Room record
    room = Room(leader_id=random.choice(selected_user_ids))
    db_session: Session = db
    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)

    # add members & history using local models to avoid circular import
    from .models import RoomMember, RoomHistory
    for uid in selected_user_ids:
        m = RoomMember(room_id=room.id, user_id=uid)
        db_session.add(m)
        h = RoomHistory(room_id=room.id, user_id=uid, action="join")
        db_session.add(h)

    db_session.commit()

    # remove selected users from queue
    remove_many_from_queue(db, selected_user_ids)

    return {
        "message": "Room created",
        "room_id": room.id,
        "leader_id": room.leader_id
    }
