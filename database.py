from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase

Base: DeclarativeBase = declarative_base()
database_url = "sqlite+pysqlite:///./sqlite3.db"
engine = create_engine(database_url, echo=True)

start_session = sessionmaker(bind=engine)

db_session = start_session()


def migrate_table_if_needs():
    Base.metadata.create_all(bind=engine)
