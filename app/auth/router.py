from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import json
import urllib.parse
from app.db.database import get_db
from app.auth import schemas, service
from app.auth.google_oauth import generate_google_login_url, get_google_user
from app.core.security import create_access_token
from app.db import models

router = APIRouter(prefix="/auth", tags=["Auth"])

# Register
@router.post("/register")
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    user = service.register_user(data, db)
    return {"message": "Register success", "user": user}

# Login
@router.post("/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    token, user = service.login_user(data, db)
    return {
        "message": "Login success",
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

# Google OAuth: Login URL
@router.get("/google/login")
def google_login():
    return {"login_url": generate_google_login_url()}

# Google OAuth Callback
@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        # 1. Ambil data user dari Google
        google_user = await get_google_user(code)
    except Exception as e:
        # Jika gagal, kembalikan error yang jelas
        raise HTTPException(status_code=400, detail=f"Google Auth Error: {str(e)}")

    email = google_user["email"]
    name = google_user.get("name", "")
    picture = google_user.get("picture", "")

    # 2. Cek apakah user sudah ada di database
    existing_user = db.query(models.User).filter(models.User.email == email).first()

    if not existing_user:
        # Jika belum ada, buat user baru
        username = email.split("@")[0]
        new_user = models.User(
            name=name,
            email=email,
            username=username,
            password="oauth_user", # Password dummy
            # pict=picture # Uncomment jika kolom pict sudah ada di model
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
    else:
        user = existing_user

    # 3. Buat Token JWT
    token = create_access_token({
        "user_id": str(user.id), # Pastikan ID dikonversi ke string
        "email": user.email
    })

    # 4. Siapkan data untuk dikirim ke Frontend
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "username": user.username,
        "avatar": picture
    }
    
    # Encode data JSON agar aman di URL
    user_data_json = json.dumps(user_data)
    encoded_user = urllib.parse.quote(user_data_json)
    
    # 5. Redirect ke halaman Frontend
    # Pastikan port 3000 atau 3001 sesuai dengan port frontend Anda yang aktif
    frontend_url = f"http://localhost:3000/auth/callback?token={token}&user={encoded_user}"
    
    return RedirectResponse(url=frontend_url)