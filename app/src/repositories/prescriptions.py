from sqlmodel import Session, select
from fastapi import Depends
from app.src.models.prescription import PrescriptionInDB, Prescription
from app.src.repositories.db import get_session


class PrescriptionRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_userid(self, userid: int) -> list[PrescriptionInDB]:
        statement = select(PrescriptionInDB).where(PrescriptionInDB.userid == userid)
        return self.db_session.exec(statement).all()

    def add_prescription(self, obj: Prescription) -> None:
        obj = PrescriptionInDB(
            userid=obj.userid,
            drugname=obj.drugname,
            times=obj.times,
            pickup_day=obj.pickup_day,
        )
        self.db_session.add(obj)
        self.db_session.commit()


def get_prescription_repo(
    db_session: Session = Depends(get_session),
) -> PrescriptionRepository:
    return PrescriptionRepository(db_session)
