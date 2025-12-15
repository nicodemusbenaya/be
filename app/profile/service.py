from sqlalchemy.orm import Session
from app.db.models import Profile
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db.models import Profile
from app.utils.redis import redis_client

def create_profile(db: Session, user_id: int, data):
    profile = Profile(
        user_id=user_id,
        name=data.name,
        birthdate=data.birthdate,
        role=data.role,
        skill=data.skill,
        pict=data.pict,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_profile_by_user(db: Session, user_id: int):
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def update_profile(db: Session, user_id: int, data):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()

    if not profile:
        return None

    profile.name = data.name
    profile.birthdate = data.birthdate
    profile.role = data.role
    profile.skill = data.skill
    profile.pict = data.pict

    db.commit()
    db.refresh(profile)
    return profile



def update_profile_picture(db: Session, user_id: int, url: str):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()

    if not profile:
        return None

    profile.pict = url
    db.commit()
    db.refresh(profile)

    # # Update Redis cache
    # redis_key = f"profile:{user_id}"
    # redis_client.hset(redis_key, "pict", url)
    # redis_client.expire(redis_key, 600)

    return profile
