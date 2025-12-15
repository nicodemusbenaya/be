from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum("active", "closed", name="room_status"), default="active")

    capacity = Column(Integer, default=6)
    current_count = Column(Integer, default=0)

    leader_id = Column(Integer, ForeignKey("auth.id"), nullable=True)
    leader = relationship("User", back_populates="rooms_led")
