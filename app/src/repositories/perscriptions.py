from sqlmodel import Session, select
from fastapi import Depends
from app.src.models.perscription import PerscriptionInDB, Perscription
from app.src.repositories.db import get_session


class PerscriptionRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_userid(self, userid: int) -> list[PerscriptionInDB]:
        statement = select(PerscriptionInDB).where(PerscriptionInDB.userid == userid)
        return self.db_session.exec(statement).all()

    def add_perscription(self, obj: Perscription) -> None:
        obj = PerscriptionInDB(
            userid=obj.userid,
            drugname=obj.drugname,
            consume_times=obj.consume_times,
            pickup_again=obj.pickup_again,
        )
        self.db_session.add(obj)
        self.db_session.commit()


def get_perscription_repo(
    db_session: Session = Depends(get_session),
) -> PerscriptionRepository:
    return PerscriptionRepository(db_session)
