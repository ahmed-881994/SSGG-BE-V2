import os
from datetime import datetime

from fastapi import APIRouter, Form, HTTPException

from app.schema.auth.auth import TokenResponse
from app.service.auth import users
from app.util.auth import compute_s256_challenge, create_access_token, generate_code

auth_codes = {}
clients = {
    "client1": {
        "client_secret": "secret1",
        "redirect_uris": ["http://localhost:8000/docs/oauth2-redirect"],
    }
}

router = APIRouter(prefix="/oauth", tags=["Auth"])


@router.post("/token", response_model=TokenResponse)
async def token():
    pass
