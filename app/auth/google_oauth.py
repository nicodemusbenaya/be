import httpx
from app.core.config import settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def generate_google_login_url():
    return (
        f"{GOOGLE_AUTH_URL}"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
    )


async def get_google_user(code: str):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            }
        )

        if token_res.status_code != 200:
            raise Exception("Failed to fetch Google token")

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise Exception("Google access token missing")

        user_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        return user_res.json()
