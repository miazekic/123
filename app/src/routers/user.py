from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.src.models.user import User, UserNoMBO
from app.src.services.auth import get_current_user
from app.src.repositories.users import UserRepository, get_user_repo

router = APIRouter()


class EnableBody(BaseModel):
    enabled: bool


class UpdateBody(BaseModel):
    mbo: str | None = None
    username: str | None = None
    password: str | None = None
    email: str | None = None
    mobile: str | None = None
    name: str | None = None
    surname: str | None = None
    receive_by_sms: bool | None = None
    receive_by_email: bool | None = None


@router.get("/account")
def user_account_info(
    current_user: User = Depends(get_current_user),
) -> User | UserNoMBO:
    if current_user.role == "patient":
        return current_user
    return UserNoMBO(
        username=current_user.username,
        email=current_user.email,
        mobile=current_user.mobile,
        name=current_user.name,
        surname=current_user.surname,
        receive_by_sms=current_user.receive_by_sms,
        receive_by_email=current_user.receive_by_email,
        role=current_user.role,
    )


# TODO: Don't make 2 DB reads (one for current_user, one in set_sms_notifications)? Maybe?
@router.post("/settings/notifications/sms")
def set_sms_notifications(
    body: EnableBody,
    repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(get_current_user),
) -> None:
    repo.set_sms_notifications(current_user.username, body.enabled)


@router.post("/settings/notifications/email")
def set_sms_notifications(
    body: EnableBody,
    repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(get_current_user),
) -> None:
    repo.set_email_notifications(current_user.username, body.enabled)


@router.post("/account/update")
def update(
    body: UpdateBody,
    repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(get_current_user),
) -> None:
    repo.update(current_user.username, body.model_dump(exclude_unset=True))
