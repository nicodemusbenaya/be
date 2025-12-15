from fastapi import FastAPI
from app.db.database import engine
from app.db import models
from app.auth.router import router as auth_router
from app.profile.router import router as profile_router
import cloudinary
from app.core.config import settings
from app.matchmaking.router import router as matchmaking_router
from app.rooms.router import router as room_router

from app.ws.router import router as ws_router

# from app.ws.voice import router as voice_router

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

models.User.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(profile_router)

app.include_router(auth_router)

app.include_router(matchmaking_router)

app.include_router(room_router)

app.include_router(ws_router)

# app.include_router(voice_router)
@app.get("/")
def home():
    return {"message": "Backend Group Match API Running"}
