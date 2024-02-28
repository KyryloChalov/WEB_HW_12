from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from static.colors import GRAY, RESET

from configparser import ConfigParser
from pathlib import Path


def get_connection_string(ini_file):
    file_config = Path(__file__).parent.joinpath(ini_file)
    config = ConfigParser()
    config.read(file_config)

    username = config.get("DB", "USER")
    password = config.get("DB", "PASSWORD")
    db_name = config.get("DB", "DATABASE")
    domain = config.get("DB", "DOMAIN")

    return f"postgresql+psycopg2://{username}:{password}@{domain}:5432/{db_name}"


def reset_db():
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine


def table_check(existing_tables) -> str:
    if existing_tables:
        result = "Tables already exist in the database:"
        for table_name in existing_tables:
            result = result + "\n\t- " + table_name
    else:
        result = "There is no table in the database"
    return result


SQLALCHEMY_DATABASE_URL = get_connection_string("db.ini")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Отримуємо список всіх таблиць (якщо вони є в бд)
tables_metadata = MetaData()
tables_metadata.reflect(bind=engine)
existing_tables = tables_metadata.tables.keys()

# print(" >>>", GRAY, table_check(existing_tables), RESET) # for debugging
if not existing_tables:
    reset_db()

SessionLocal = sessionmaker(
    expire_on_commit=True, autocommit=False, autoflush=False, bind=engine
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
