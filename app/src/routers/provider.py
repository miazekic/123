from fastapi import APIRouter, Depends, HTTPException
from app.src.models.user import UserForProviders
from app.src.repositories.users import UserRepository, get_user_repo
from app.src.repositories.perscriptions import (
    PerscriptionRepository,
    get_perscription_repo,
)
from app.src.services.auth import get_current_user
from app.src.models.user import UserInternal
from app.src.models.perscription import Perscription, PerscriptionPublic
from pydantic import BaseModel
from datetime import date

router = APIRouter()


@router.get("/patients/{mbo}")
def patient_info(
    mbo: str,
    repo: UserRepository = Depends(get_user_repo),
    user: UserInternal = Depends(get_current_user),
):
    if user.role != "provider":
        raise HTTPException(
            status_code=401, detail="User not authorized to perform this operation"
        )
    patient_db = repo.get_by_mbo(mbo)
    if not patient_db:
        raise HTTPException(status_code=400, detail="Patient not found")
    return UserForProviders(
        mbo=patient_db.mbo,
        email=patient_db.email,
        mobile=patient_db.mobile,
        name=patient_db.name,
        surname=patient_db.surname,
    )


@router.get("/patients/{mbo}/treatments")
def patient_perscriptions(
    mbo: str,
    user_repo: UserRepository = Depends(get_user_repo),
    perscription_repo: PerscriptionRepository = Depends(get_perscription_repo),
    user: UserInternal = Depends(get_current_user),
):
    if user.role != "provider":
        raise HTTPException(
            status_code=401, detail="User not authorized to perform this operation"
        )
    patient_db = user_repo.get_by_mbo(mbo)
    if not patient_db:
        raise HTTPException(status_code=400, detail="Patient not found")
    persctiptions_db = perscription_repo.get_by_userid(patient_db.userid)
    return [
        PerscriptionPublic(
            drugName=p.drugname,
            times=p.times,
            pickupDay=p.pickup_day,
        )
        for p in persctiptions_db
    ]


class PerscriptionBody(BaseModel):
    patientMbo: str
    drugName: str
    times: list[str]
    pickupDay: date


@router.post("/perscription")
def add_perscription(
    body: PerscriptionBody,
    user_repo: UserRepository = Depends(get_user_repo),
    perscription_repo: PerscriptionRepository = Depends(get_perscription_repo),
    user: UserInternal = Depends(get_current_user),
):
    if user.role != "provider":
        raise HTTPException(
            status_code=401, detail="User not authorized to perform this operation"
        )
    patient_db = user_repo.get_by_mbo(body.patientMbo)
    if not patient_db:
        raise HTTPException(status_code=400, detail="Patient not found")
    perscription = Perscription(
        userid=patient_db.userid,
        drugname=body.drugName,
        times=body.times,
        pickup_day=body.pickupDay,
    )
    perscription_repo.add_perscription(perscription)
