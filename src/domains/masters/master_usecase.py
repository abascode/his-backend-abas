from typing import List

from fastapi.params import Depends
from starlette.requests import Request

from src.domains.forecasts.forecast_interface import IForecastRepository
from src.domains.forecasts.forecast_repository import ForecastRepository
from src.domains.masters.master_interface import IMasterUseCase, IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.models.requests.master_request import GetOrderConfigurationRequest, GetStockPilotRequest
from src.models.responses.basic_response import TextValueResponse
from src.models.responses.master_response import OrderConfigurationsResponse, StockPilotsResponse


class MasterUseCase(IMasterUseCase):

    def __init__(
        self,
        forecast_repo: IForecastRepository = Depends(ForecastRepository),
        master_repo: IMasterRepository = Depends(MasterRepository),
    ):
        self.forecast_repo = forecast_repo
        self.master_repo = master_repo

    def get_dealer_options(
            self,
            request: Request,
            search: str | None = None
    ) -> List[TextValueResponse]:
        dealers = self.master_repo.get_dealer_options(request,search)

        return [
            TextValueResponse(
                text=i.name,
                value = i.id,
            )
            for i in dealers

        ]

    def get_model_options(
            self,
            request: Request,
            search: str | None = None
    ) -> List[TextValueResponse]:
        models = self.master_repo.get_model_options(request,search)

        return [
            TextValueResponse(
                text=i.id,
                value = i.id,
            )
            for i in models

        ]

    def get_order_configuration(
            self,
            request: Request,
            order_configuration: GetOrderConfigurationRequest
    ) -> List[OrderConfigurationsResponse]:
        orders = self.master_repo.get_order_configuration(request,order_configuration.month,order_configuration.year)

        return [
            OrderConfigurationsResponse(
                category_id= i.category_id,
                forecast_percentage= i.forecast_percentage,
                urgent_percentage= i.urgent_percentage,
            )
            for i in orders
        ]

    def get_stock_pilots(
            self,
            request: Request,
            stock_pilots: GetStockPilotRequest
    ) -> List[StockPilotsResponse]:
        stock_pilots = self.master_repo.get_stock_pilots(request,stock_pilots.month,stock_pilots.year)

        return [
            StockPilotsResponse(
                segment_id= i.segment_id,
                percentage= i.percentage,
            )
            for i in stock_pilots
        ]