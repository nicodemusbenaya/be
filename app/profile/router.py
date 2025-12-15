
from fastapi import File, UploadFile, Form
# from app.utils.cloudinary_upload import upload_image
from app.core.security import get_current_user

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from .schemas import ProfileCreate, ProfileOut
from .service import (
    create_profile,
    get_profile_by_user,
    update_profile,
    update_profile_picture
)
from .upload_service import upload_avatar


router = APIRouter(prefix="/profile", tags=["Profile"])



# UPLOAD AVATAR
@router.post("/upload-avatar")
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Upload avatar ke Cloudinary dan update profile user
    """

    # Upload ke Cloudinary
    url = await upload_avatar(file)

    # Simpan ke database
    updated = update_profile_picture(db, current_user.id, url)

    if not updated:
        raise HTTPException(404, "Profile not found")

    return {"avatar_url": url}



# CREATE Profile (hanya 1x)
@router.post("/", response_model=ProfileOut)
def create_user_profile(
    data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing = get_profile_by_user(db, current_user.id)

    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = create_profile(db, current_user.id, data)
    return profile



# GET Profile user sendiri
@router.get("/me", response_model=ProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = get_profile_by_user(db, current_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile



# UPDATE Profile user
@router.put("/", response_model=ProfileOut)
def update_my_profile(
    data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = update_profile(db, current_user.id, data)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile
