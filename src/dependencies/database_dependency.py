from typing import Generator
from sqlalchemy.orm import Session
from src.infrastructures.databases.database import postgres


def get_va_db() -> Generator[Session, None, None]:
    db = postgres("vehicle_allocation")
    try:
        yield db
    finally:
        db.close()
