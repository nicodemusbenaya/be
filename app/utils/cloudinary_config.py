import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Konfigurasi Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_image(file):
    """Upload foto ke Cloudinary dan return URL"""
    result = cloudinary.uploader.upload(file)
    return result.get("secure_url")
