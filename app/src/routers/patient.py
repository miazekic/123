from fastapi import APIRouter, Depends, HTTPException
from app.src.services.auth import get_current_user
from app.src.repositories.prescriptions import (
    PrescriptionRepository,
    get_prescription_repo,
)
from app.src.models.user import UserInternal
from app.src.models.prescription import PrescriptionPublic

router = APIRouter()


@router.get("/treatments")
def patient_treatments(
    user: UserInternal = Depends(get_current_user),
    repo: PrescriptionRepository = Depends(get_prescription_repo),
):
    if user.role != "patient":
        raise HTTPException(
            status_code=403,
            detail="Treatment list only available for users with 'patient' role",
        )
    treatments = repo.get_by_userid(user.userid)
    return [
        PrescriptionPublic(
            drugName=p.drugname,
            times=p.times,
            pickupDay=p.pickup_day,
        )
        for p in treatments
    ]
