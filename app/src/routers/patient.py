from fastapi import APIRouter, Depends, HTTPException
from app.src.services.auth import get_current_user
from app.src.repositories.perscriptions import (
    PerscriptionRepository,
    get_perscription_repo,
)
from app.src.models.user import UserInternal
from app.src.models.perscription import PerscriptionPublic

router = APIRouter()


@router.get("/treatments")
def patient_treatments(
    user: UserInternal = Depends(get_current_user),
    repo: PerscriptionRepository = Depends(get_perscription_repo),
):
    if user.role != "patient":
        raise HTTPException(
            status_code=403,
            detail="Treatment list only available for users with 'patient' role",
        )
    treatments = repo.get_by_userid(user.userid)
    return [
        PerscriptionPublic(
            drugname=p.drugname,
            consume_times=p.consume_times,
            pickup_again=p.pickup_again,
        )
        for p in treatments
    ]
