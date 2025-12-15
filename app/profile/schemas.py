from pydantic import BaseModel
from datetime import date
from typing import Optional


class ProfileCreate(BaseModel):
    name: str
    birthdate: date
    role: str
    skill: str
    pict: Optional[str] = None  


class ProfileOut(BaseModel):
    id: int
    user_id: int
    name: str
    birthdate: date
    role: str
    skill: str
    pict: Optional[str]

    class Config:
        orm_mode = True
