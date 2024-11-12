# -*- coding: utf-8 -*-
import abc
from typing import List

from src.domains.master.entities.va_dealer import Dealer
from src.domains.master.entities.va_model import Model
from src.models.responses.basic_response import TextValueResponse
from starlette.requests import Request
from src.domains.master.entities.va_segment import Segment


class IMasterUseCase:
    @abc.abstractmethod
    def get_dealer_options(
        self, request: Request, keyword: str
    ) -> List[TextValueResponse]:
        pass
    
    @abc.abstractmethod
    def get_forecast_order(
        self, request: Request
    ) -> List[TextValueResponse]:
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
    def get_dealer_options(self, request: Request, keyword: str) -> List[Dealer]:
        pass
    
    @abc.abstractmethod
    def get_forecast_order(self, request: Request) -> List[Segment]:
        pass
