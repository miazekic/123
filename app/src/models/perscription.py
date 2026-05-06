from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column
from datetime import date


class PerscriptionInDB(SQLModel, table=True):
    __tablename__ = "perscriptions"

    perscriptionid: int = Field(primary_key=True)
    userid: int
    drugname: str
    consume_times: list[str] = Field(sa_column=Column(JSON))
    pickup_again: date


class Perscription(BaseModel):
    userid: int
    drugname: str
    consume_times: list[str]
    pickup_again: date


class PerscriptionPublic(BaseModel):
    drugname: str
    consume_times: list[str]
    pickup_again: date
