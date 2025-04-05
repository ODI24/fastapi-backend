from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# ⬇️ ACEPTA PARAMETRO return_to EN LA URL
@app.get("/auth/google")
def login_with_google(return_to: str = ""):
    # Guardamos temporalmente el return_to como parte del redirect_uri usando el estado
    redirect = (
        f"{AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&state={return_to}"
    )
    return RedirectResponse(redirect)


@app.get("/auth/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    return_to = request.query_params.get("state")  # Recuperamos IP desde `state`
    
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
    
    print("TOKENS:", tokens)  # para depuración
    
    id_token = tokens.get("id_token")
    access_token = tokens.get("access_token")

    # Si no se pasó IP, redirigimos a default (Expo Go en iPhone por ejemplo)
    redirect_to_app = return_to or "exp://exp.host/@andrewoliverbatta/AppEstudio"

    # Le agregamos los tokens a la URL
    redirect_to_app += f"?access_token={access_token}&id_token={id_token}"

    return RedirectResponse(redirect_to_app)
