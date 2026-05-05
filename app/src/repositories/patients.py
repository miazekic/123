from sqlmodel import Session, select
from app.src.models.patient import PatientInDB


class PatientRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_mbo(self, mbo: str) -> PatientInDB:
        statement = select(PatientInDB).where(PatientInDB.mbo == mbo)
        return self.db_session.exec(statement).first()
