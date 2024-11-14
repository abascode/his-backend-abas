# -*- coding: utf-8 -*-
import abc
from typing import List

from src.domains.master.entities.va_dealer import Dealer
from src.domains.master.entities.va_model import Model
from src.models.responses.basic_response import TextValueResponse
from starlette.requests import Request

from src.models.responses.master_response import StockPilotResponse

from src.domains.master.entities.va_segment import Segment
from src.models.responses.forecast_response import ForecastOrderResponse

class IMasterUseCase:
    @abc.abstractmethod
    def get_dealer_options(
        self, request: Request, keyword: str
    ) -> List[TextValueResponse]:
        pass

    @abc.abstractmethod
    def get_forecast_orders(
        self, request: Request
    ) -> List[ForecastOrderResponse]:
        pass

    @abc.abstractmethod
    def get_urgent_orders(
        self, request: Request
    ) -> List[ForecastOrderResponse]:
        pass

    @abc.abstractmethod
    def get_stock_pilots(
        self, request: Request, year: int, month: int
    ) -> List[StockPilotResponse]:
        pass


class IMasterRepository:
    @abc.abstractmethod
    def get_dealer_list(self, request: Request, keyword: str) -> List[Dealer]:
        pass

    @abc.abstractmethod
    def first_or_create_dealer(self, request: Request, name: str) -> Dealer:
        pass

    @abc.abstractmethod
    def find_model(self, request: Request, name: str | None = None) -> Model | None:
        pass

    @abc.abstractmethod
    def get_stock_pilots(
        self, request: Request, year: int, month: int
    ) -> List[StockPilotResponse]:
        pass

    @abc.abstractmethod
    def get_dealer_options(self, request: Request, keyword: str) -> List[Dealer]:
        pass

    @abc.abstractmethod
    def get_forecast_orders(self, request: Request) -> List[Segment]:
        pass

    @abc.abstractmethod
    def get_urgent_orders(self, request: Request) -> List[Segment]:
        pass
