from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_models import Model
from src.domains.masters.master_interface import IMasterRepository


class MasterRepository(IMasterRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return (
            request.state.va_db if request.state.va_db is not None else self.va_db
        )
        
    def find_model_by_variant(self, request: Request, variant: str) -> Model | None:
        return self.get_va_db(request).query(Model).filter(Model.variant == variant).first()
        

    def find_model(self, request: Request, model_id: str) -> Model | None:
        return self.get_va_db(request).query(Model).filter(Model.id == model_id).first()

    def upsert_dealer(self, request: Request, dealer: Dealer) -> Dealer | None:
        temp = (
            self.get_va_db(request).query(Dealer).filter(Dealer.id == dealer.id).first()
        )
        if temp is None:
            self.get_va_db(request).add(dealer)
            self.get_va_db(request).flush()
        else:
            temp.name = dealer.name
        return dealer
