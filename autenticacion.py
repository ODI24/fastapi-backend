from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # Debe ser https://<TU_BACKEND>.onrender.com/auth/callback

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

@app.get("/auth/google")
def login_with_google():
    redirect = (
        f"{AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
    )
    return RedirectResponse(redirect)

@app.get("/auth/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No se recibió código"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        return {"error": "Error al intercambiar el código", "details": response.text}

    tokens = response.json()
    id_token = tokens.get("id_token")
    access_token = tokens.get("access_token")

    # Redirigir a la app Expo con los tokens
    redirect_to_app = (
        f"exp://exp.host/@andrewoliverbatta/AppEstudio"
        f"?access_token={access_token}&id_token={id_token}"
    )

    return RedirectResponse(redirect_to_app)
