from typing import List

from fastapi.params import Depends
from starlette.requests import Request

from src.domains.forecasts.forecast_interface import IForecastRepository
from src.domains.forecasts.forecast_repository import ForecastRepository
from src.domains.masters.master_interface import IMasterUseCase, IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.models.responses.basic_response import TextValueResponse


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

