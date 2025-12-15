from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 1. Import Middleware
from app.db.database import engine
from app.db import models
from app.auth.router import router as auth_router
from app.profile.router import router as profile_router
import cloudinary
from app.core.config import settings
from app.matchmaking.router import router as matchmaking_router
from app.rooms.router import router as room_router
from app.ws.router import router as ws_router

# Konfigurasi Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# Buat tabel database
models.User.metadata.create_all(bind=engine)

app = FastAPI()

# 2. KONFIGURASI CORS (PENTING!)
# Masukkan semua kemungkinan port frontend Anda (3000 dan 3001)
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(profile_router)
app.include_router(auth_router)
app.include_router(matchmaking_router)
app.include_router(room_router)
app.include_router(ws_router)

@app.get("/")
def home():
    return {"message": "Backend Group Match API Running"}