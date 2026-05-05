from sqlmodel import Session, select
from app.src.models.user import UserInDB


class UserRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_mbo(self, mbo: str) -> UserInDB:
        statement = select(UserInDB).where(UserInDB.mbo == mbo)
        return self.db_session.exec(statement).first()
