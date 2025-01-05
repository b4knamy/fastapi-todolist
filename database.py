from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, create_engine, SQLModel
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from pathlib import Path
import os

parent_dir = Path(__file__).resolve().parent
load_dotenv(parent_dir / ".env")

is_test = os.environ.get("USE_DATABASE_TEST", 0)

if is_test == 1:
    sqlite_url = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///sqlite3_test.db")
else:
    sqlite_url = os.environ.get("DATABASE_URL", "sqlite:///sqlite3.db")


connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
