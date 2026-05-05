from sqlmodel import Session, select
from fastapi import Depends
from app.src.models.user import UserInDB
from app.src.repositories.db import get_session


class UserRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_mbo(self, mbo: str) -> UserInDB:
        statement = select(UserInDB).where(UserInDB.mbo == mbo)
        return self.db_session.exec(statement).first()

    def get_by_username(self, username: str) -> UserInDB:
        statement = select(UserInDB).where(UserInDB.username == username)
        return self.db_session.exec(statement).first()


def get_user_repo(db_session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(db_session)
