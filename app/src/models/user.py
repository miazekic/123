from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class UserInDB(SQLModel, table=True):
    __tablename__ = "users"

    userid: int = Field(primary_key=True)
    mbo: str | None
    username: str
    password: str
    email: str
    mobile: str
    name: str
    surname: str
    receive_by_sms: bool = False
    receive_by_email: bool = False
    role: str


class UserInternal(BaseModel):
    userid: int
    mbo: str
    username: str
    email: str
    mobile: str
    name: str
    surname: str
    receive_by_sms: bool = False
    receive_by_email: bool = False
    role: str


class UserPersonal(BaseModel):
    mbo: str | None
    username: str
    email: str
    mobile: str
    name: str
    surname: str
    receive_by_sms: bool
    receive_by_email: bool
    role: str


class UserPersonalNoMBO(BaseModel):
    username: str
    email: str
    mobile: str
    name: str
    surname: str
    receive_by_sms: bool
    receive_by_email: bool
    role: str


class UserForProviders(BaseModel):
    mbo: str
    email: str
    mobile: str
    name: str
    surname: str
