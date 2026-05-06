from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column
from datetime import date


class PrescriptionInDB(SQLModel, table=True):
    __tablename__ = "prescriptions"

    prescriptionid: int = Field(primary_key=True)
    userid: int
    drugname: str
    times: list[str] = Field(sa_column=Column(JSON))
    pickup_day: date


class Prescription(BaseModel):
    userid: int
    drugname: str
    times: list[str]
    pickup_day: date


class PrescriptionPublic(BaseModel):
    drugName: str
    times: list[str]
    pickupDay: date
