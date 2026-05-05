from sqlmodel import Session, select
from fastapi import Depends
from app.src.models.user import UserInDB
from app.src.repositories.db import get_session
from fastapi import HTTPException


class UserRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_mbo(self, mbo: str) -> UserInDB:
        statement = select(UserInDB).where(UserInDB.mbo == mbo)
        return self.db_session.exec(statement).first()

    def get_by_username(self, username: str) -> UserInDB:
        statement = select(UserInDB).where(UserInDB.username == username)
        return self.db_session.exec(statement).first()

    def set_sms_notifications(self, username: str, enabled: bool) -> None:
        statement = select(UserInDB).where(UserInDB.username == username)
        user = self.db_session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        user.receive_by_sms = enabled
        self.db_session.add(user)
        self.db_session.commit()

    def set_email_notifications(self, username: str, enabled: bool) -> None:
        statement = select(UserInDB).where(UserInDB.username == username)
        user = self.db_session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        user.receive_by_email = enabled
        self.db_session.add(user)
        self.db_session.commit()

    def update(self, username: str, params_to_update: dict[str, any]) -> None:
        statement = select(UserInDB).where(UserInDB.username == username)
        user = self.db_session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        for key, value in params_to_update.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.db_session.add(user)
        self.db_session.commit()


def get_user_repo(db_session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(db_session)
