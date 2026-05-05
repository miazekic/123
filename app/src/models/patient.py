from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class PatientInDB(SQLModel, table=True):
    __tablename__ = "patients"

    mbo: str = Field(primary_key=True)
    username: str
    password: str
    email: str
    mobile: str
    name: str
    surname: str
    receive_by_sms: bool = False
    receive_by_email: bool = False


class PatientPersonal(BaseModel):
    mbo: str
    username: str
    email: str
    mobile: str
    name: str
    surname: str
    receive_by_sms: bool
    receive_by_email: bool


class PatientForProviders(BaseModel):
    mbo: str
    email: str
    mobile: str
    name: str
    surname: str
