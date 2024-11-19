from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.masters.entities.va_models import Model
from src.domains.masters.master_interface import IMasterRepository


class MasterRepository(IMasterRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return (
            request.state.va_db if request.state.va_db is not None else self.get_va_db
        )

    def find_model(self, request: Request, model_id: str) -> Model | None:
        return self.get_va_db(request).query(Model).filter(Model.id == model_id).first()
