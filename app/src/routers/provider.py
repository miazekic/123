from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.src.models.patient import PatientForProviders
from app.src.repositories.patients import PatientRepository
from app.src.repositories.db import get_session


def get_patient_repo(db_session: Session = Depends(get_session)) -> PatientRepository:
    return PatientRepository(db_session)


router = APIRouter()


@router.get("/patients/{mbo}")
def patient_info(mbo: str, repo: PatientRepository = Depends(get_patient_repo)):
    patient_db = repo.get_by_mbo(mbo)
    if not patient_db:
        raise HTTPException(status_code=400, detail="Patient not found")
    return PatientForProviders(
        mbo=patient_db.mbo,
        email=patient_db.email,
        mobile=patient_db.mobile,
        name=patient_db.name,
        surname=patient_db.surname,
    )
