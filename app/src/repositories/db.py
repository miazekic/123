from typing import Generator
from sqlmodel import create_engine, Session
import os

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")
DB_PROTOCOL = os.environ.get("DB_PROTOCOL")
DB_NAME = os.environ.get("DB_NAME")

engine = create_engine(
    DB_PROTOCOL + "://" + DB_USER + ":" + DB_PASS + "@" + DB_URL + "/" + DB_NAME
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
