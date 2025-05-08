from fastapi import APIRouter

from app.schema.auth.auth import TokenResponse

router = APIRouter(prefix="/oauth", tags=["Auth"])


@router.post("/token", response_model=TokenResponse)
async def token():
    pass
