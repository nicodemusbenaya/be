from sqlalchemy.orm import Session
from .models import MatchmakingQueue

def add_to_queue(db: Session, user_id: int, role: str):
    entry = MatchmakingQueue(user_id=user_id, role=role)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def is_in_queue(db: Session, user_id: int):
    return db.query(MatchmakingQueue).filter_by(user_id=user_id).first()

def count_queue(db: Session):
    return db.query(MatchmakingQueue).count()

def get_all_queue(db: Session):
    return db.query(MatchmakingQueue).all()

def get_queue_by_role(db: Session, role: str):
    return db.query(MatchmakingQueue).filter_by(role=role).all()

def remove_from_queue(db: Session, user_id: int):
    db.query(MatchmakingQueue).filter_by(user_id=user_id).delete()
    db.commit()

def remove_many_from_queue(db: Session, user_ids: list[int]):
    db.query(MatchmakingQueue).filter(MatchmakingQueue.user_id.in_(user_ids)).delete(synchronize_session=False)
    db.commit()

def clear_queue(db: Session):
    db.query(MatchmakingQueue).delete()
    db.commit()
