from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.database import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    profile = relationship("Profile", back_populates="user", uselist=False)

    rooms_led = relationship("Room", back_populates="leader")


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("auth.id"), unique=True)  # 1 user = 1 profile

    name = Column(String(100))
    birthdate = Column(Date)
    role = Column(String(50))
    pict = Column(String(255))  # URL foto profil
    skill = Column(String(255))  # bisa disimpan comma-separated "Python,Vue,SQL"

    user = relationship("User", back_populates="profile")