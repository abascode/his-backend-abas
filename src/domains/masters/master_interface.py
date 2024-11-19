import abc
from typing import List

from starlette.requests import Request

from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_models import Model
from src.domains.masters.entities.va_order_configurations import OrderConfiguration
from src.domains.masters.entities.va_stock_pilots import StockPilot
from src.models.requests.master_request import GetOrderConfigurationRequest, GetStockPilotRequest
from src.models.responses.basic_response import TextValueResponse
from src.models.responses.master_response import OrderConfigurationsResponse, StockPilotsResponse


class IMasterUseCase:

    @abc.abstractmethod
    def get_dealer_options(self, request:Request, search: str
    ) -> List[TextValueResponse]:
        pass

    @abc.abstractmethod
    def get_model_options(self, request:Request, search: str
    ) -> List[TextValueResponse]:
        pass

    @abc.abstractmethod
    def get_order_configuration(self, request, order_configuration:GetOrderConfigurationRequest
    )-> List[OrderConfigurationsResponse]:
        pass


    @abc.abstractmethod
    def get_stock_pilots(self, request, stock_pilots:GetStockPilotRequest
    )-> List[StockPilotsResponse]:
        pass


class IMasterRepository:
    @abc.abstractmethod
    def find_model(self, request: Request, model_id: str) -> Model | None:
        pass

    @abc.abstractmethod
    def upsert_dealer(self, request: Request, dealer: Dealer) -> Dealer | None:
        pass

    @abc.abstractmethod
    def get_dealer_options(self, request: Request, search: str) -> List[Dealer]:
        pass

    @abc.abstractmethod
    def get_model_options(self, request: Request, search: str) -> List[Model]:
        pass

    @abc.abstractmethod
    def get_order_configuration(self, request: Request, month:int, year:int) -> List[OrderConfiguration]:
        pass

    @abc.abstractmethod
    def get_stock_pilots(self, request: Request, month: int, year: int) -> List[StockPilot]:
        pass