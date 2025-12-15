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
    # PERBAIKAN 1: Gunakan RedirectResponse agar langsung ke halaman Google
    return RedirectResponse(url=generate_google_login_url())

# Google OAuth Callback
@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        # 1. Ambil data user dari Google
        google_user = await get_google_user(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Auth Error: {str(e)}")

    email = google_user.get("email")
    name = google_user.get("name", "")
    picture = google_user.get("picture", "")

    # 2. Cek apakah user sudah ada
    existing_user = db.query(models.User).filter(models.User.email == email).first()

    if not existing_user:
        username = email.split("@")[0]

        # PERBAIKAN 2: Buat User TANPA field 'name' (karena 'name' ada di Profile)
        new_user = models.User(
            email=email,
            username=username,
            password="oauth_user", # Password dummy
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user) # Dapatkan ID user baru

        # PERBAIKAN 3: Buat Profile secara manual dan hubungkan ke User
        new_profile = models.Profile(
            user_id=new_user.id,
            name=name,      # Simpan nama di tabel Profile
            pict=picture,   # Simpan foto di tabel Profile
            role="Member",  # Default role
            skill=""        # Default skill kosong
        )
        db.add(new_profile)
        db.commit()
        
        user = new_user
    else:
        user = existing_user

    # 3. Buat Token JWT
    token = create_access_token({
        "user_id": str(user.id),
        "email": user.email
    })

    # 4. Siapkan data untuk dikirim ke Frontend
    # Ambil nama dari profile jika user sudah ada
    display_name = user.profile.name if user.profile else name
    display_pict = user.profile.pict if user.profile else picture

    user_data = {
        "id": str(user.id),
        "email": user.email,
        "name": display_name,
        "username": user.username,
        "avatar": display_pict
    }
    
    # Encode data JSON agar aman di URL
    user_data_json = json.dumps(user_data)
    encoded_user = urllib.parse.quote(user_data_json)
    
    # 5. Redirect ke halaman Frontend
    # Pastikan port sesuai (3000 atau 3001)
    frontend_url = f"http://localhost:3000/auth/callback?token={token}&user={encoded_user}"
    
    return RedirectResponse(url=frontend_url)