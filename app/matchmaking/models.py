from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.database import Base

# queue table
class MatchmakingQueue(Base):
    __tablename__ = "matchmaking_queue"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"))
    role = Column(String(50))
    joined_at = Column(TIMESTAMP)

    user = relationship("User")  # expects class User in app.db.models


class RoomMember(Base):
    __tablename__ = "room_members"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"))


class RoomHistory(Base):
    __tablename__ = "room_history"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"))
    action = Column(Enum("join", "leave", "closed", name="history_action"))
    timestamp = Column(TIMESTAMP)
