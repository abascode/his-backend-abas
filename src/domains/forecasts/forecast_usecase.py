from typing import List

from fastapi import Depends
from starlette.requests import Request

from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.forecast_interface import (
    IForecastUseCase,
    IForecastRepository,
)
from src.domains.forecasts.forecast_repository import ForecastRepository
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.master_interface import IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.models.requests.forecast_request import CreateForecastRequest
from src.shared.enums import Database
from src.shared.utils.database_utils import begin_transaction, commit


class ForecastUseCase(IForecastUseCase):

    def __init__(
        self,
        forecast_repo: IForecastRepository = Depends(ForecastRepository),
        master_repo: IMasterRepository = Depends(MasterRepository),
    ):
        self.forecast_repo = forecast_repo
        self.master_repo = master_repo

    def create_forecast(
        self, request: Request, create_forecast_request: CreateForecastRequest
    ) -> None:
        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        forecast = self.forecast_repo.find_forecast(
            request, create_forecast_request.record_id
        )
        dealer = self.master_repo.upsert_dealer(
            request,
            Dealer(
                id=create_forecast_request.dealer_code,
                name=create_forecast_request.dealer_name,
            ),
        )
        if forecast is None:
            self.forecast_repo.create_forecast(Forecast())
        else:
            forecast.id = create_forecast_request.record_id
            forecast.name = create_forecast_request.record_name
            forecast.dealer_id = dealer.id
            forecast.year = create_forecast_request.year
            forecast.month = create_forecast_request.month

            for i in create_forecast_request.details:
                if i

        commit(request, Database.VEHICLE_ALLOCATION)

    def convert_n_to_months(self, request: Request, detail: dict) -> List[ForecastDetail]:
