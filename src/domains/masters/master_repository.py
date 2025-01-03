from typing import List, Type

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.masters.entities.va_categories import Category
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_models import Model
from src.domains.masters.entities.va_order_configurations import OrderConfiguration
from src.domains.masters.entities.va_segments import Segment
from src.domains.masters.entities.va_stock_pilots import StockPilot
from src.domains.masters.master_interface import IMasterRepository


class MasterRepository(IMasterRepository):
    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return request.state.va_db if request.state.va_db is not None else self.va_db

    def find_model_by_variant(self, request: Request, variant: str) -> Model | None:
        return (
            self.get_va_db(request)
            .query(Model)
            .filter(Model.variant == variant)
            .first()
        )

    def find_category(self, request: Request, category_id: str) -> Model | None:
        return (
            self.get_va_db(request)
            .query(Category)
            .filter(Category.id == category_id)
            .first()
        )

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

    def find_dealer(
        self, request: Request, name: str = None, dealer_id: str = None
    ) -> Dealer | None:
        query = self.get_va_db(request).query(Dealer)

        if name is not None:
            query = query.filter(Dealer.name == name)
        if dealer_id is not None:
            query = query.filter(Dealer.id == dealer_id)

        return query.first()

    def get_dealer_options(self, request: Request, search: str) -> List[Dealer]:
        dealer = (
            self.get_va_db(request)
            .query(Dealer)
            .filter(Dealer.name.ilike("%" + search + "%"))
            .all()
        )
        if dealer is not None:
            return dealer

    def get_model_options(self, request: Request, search: str) -> list[Type[Model]]:
        return (
            self.get_va_db(request)
            .query(Model)
            .filter(Model.id.ilike("%" + search + "%"))
            .all()
        )

    def get_order_configuration(
        self, request: Request, month: int, year: int
    ) -> List[OrderConfiguration]:
        order = (
            self.get_va_db(request)
            .query(OrderConfiguration)
            .filter(OrderConfiguration.month == month, OrderConfiguration.year == year)
            .all()
        )
        return order

    def get_stock_pilots(
        self, request: Request, month: int, year: int
    ) -> List[StockPilot]:
        stock_pilots = (
            self.get_va_db(request)
            .query(StockPilot)
            .filter(StockPilot.month == month, StockPilot.year == year)
            .all()
        )
        return stock_pilots

    def get_segment_options(self, request: Request, search: str) -> list[Type[Segment]]:
        return (
            self.get_va_db(request)
            .query(Segment)
            .filter(Segment.id.ilike("%" + search + "%"))
            .all()
        )

    def get_category_options(
        self, request: Request, search: str
    ) -> list[Type[Category]]:
        return (
            self.get_va_db(request)
            .query(Category)
            .filter(Category.id.ilike("%" + search + "%"))
            .all()
        )
