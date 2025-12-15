from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db import models
from app.utils.hash import hash_password, verify_password
from app.core.security import create_access_token

def register_user(data, db: Session):

    # cek confirm password
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # cek email
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Email already used")

    # cek username
    if db.query(models.User).filter_by(username=data.username).first():
        raise HTTPException(status_code=400, detail="Username already used")

    hashed = hash_password(data.password)

    new_user = models.User(
        email=data.email,
        username=data.username,
        password=hashed
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(data, db: Session):
    user = db.query(models.User).filter_by(email=data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # generate jwt
    token = create_access_token({
        "user_id": user.id,
        "email": user.email
    })

    return token, user
