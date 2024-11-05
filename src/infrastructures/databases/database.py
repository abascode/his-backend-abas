from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.config import get_config


def postgres(name: str) -> Session:
    engine = create_engine(
        "postgresql+psycopg2://{username}:{password}@{host}:{port}/{name}".format(
            **get_config().database[name].__dict__
        )
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    return db
