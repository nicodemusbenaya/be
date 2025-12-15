import cloudinary.uploader

async def upload_avatar(file):
    result = cloudinary.uploader.upload(
        file.file,
        folder="groupmatch/avatar"
    )
    return result.get("secure_url")
