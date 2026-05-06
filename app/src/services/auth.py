from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from jose import jwt
from passlib.context import CryptContext
from app.src.models.user import UserInternal
from app.src.repositories.users import UserRepository, get_user_repo
import os

SECRET_KEY = os.environ.get("SECRET_KEY")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer("/token")


# TODO: Add expiry
def create_access_token(username: str) -> str:
    return jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")


def authenticate_user(
    repo: UserRepository = Depends(get_user_repo),
    credentials: OAuth2PasswordRequestForm = Depends(),
) -> bool:
    user_db = repo.get_by_username(credentials.username)
    if not user_db or not pwd_context.verify(credentials.password, user_db.password):
        return False
    return True


def get_current_user(
    token: str = Depends(oauth2_scheme), repo: UserRepository = Depends(get_user_repo)
) -> UserInternal:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        username: str = payload.get("username")
        if not username:
            raise HTTPException(status_code=401, detail="Could not validate token")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate token")

    user_db = repo.get_by_username(username)
    if not user_db:
        raise HTTPException(status_code=401, detail="Could not validate token")
    return UserInternal(
        userid=user_db.userid,
        username=user_db.username,
        email=user_db.email,
        mobile=user_db.mobile,
        role=user_db.role,
        mbo=user_db.mbo,
        name=user_db.name,
        surname=user_db.surname,
        receive_by_sms=user_db.receive_by_sms,
        receive_by_email=user_db.receive_by_email,
    )
