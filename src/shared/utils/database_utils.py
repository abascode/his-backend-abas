from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.shared.enums import Database


def commit(request: Request, database: Database):
    if database == Database.VEHICLE_ALLOCATION:
        request.state.va_db.commit()
        request.state.va_db = None


def rollback_all(request: Request):
    try:
        request.state.va_db.rollback()
        request.state.va_db = None
    except Exception as ex:
        pass


def begin_transaction(request: Request, database: Database):
    if database == Database.VEHICLE_ALLOCATION and request.state.va_db is None:
        request.state.va_db = next(get_va_db())
