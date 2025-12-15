from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")




def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        "exp": expire,
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")
        email = payload.get("email")

        if not user_id and not email:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    else:
        user = db.query(User).filter(User.email == email).first()

    if not user:
        raise credentials_exception

    return user

