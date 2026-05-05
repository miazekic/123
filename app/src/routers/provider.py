from fastapi import APIRouter, Depends, HTTPException
from app.src.models.user import UserForProviders
from app.src.repositories.users import UserRepository, get_user_repo
from app.src.services.auth import get_current_user
from app.src.models.user import User

router = APIRouter()


@router.get("/patients/{mbo}")
def patient_info(
    mbo: str,
    repo: UserRepository = Depends(get_user_repo),
    user: User = Depends(get_current_user),
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
