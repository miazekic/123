from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.src.services.auth import authenticate_user, create_access_token

router = APIRouter()


@router.post("/token")
def authenticate(
    authenticated: bool = Depends(authenticate_user),
    credentials: OAuth2PasswordRequestForm = Depends(),
) -> None:
    if not authenticated:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return create_access_token(credentials.username)
