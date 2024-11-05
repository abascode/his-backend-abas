from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.domains.forecast.forecast_interface import IForecastUseCase
from src.domains.forecast.forecast_usecase import ForecastUseCase
from src.models.requests.forecast_request import UpsertForecastRequest
from src.models.responses.auth_response import LoginResponse
from src.models.responses.basic_response import NoDataResponse

router = APIRouter(prefix="/api/forecast", tags=["Forecast"])


@router.post(
    "",
    response_model=NoDataResponse,
    summary="Create Forecast",
    description="Create forecast, if the id exists in the database, the forecast will be overwritten",
)
def create_forecast(
    request: Request,
    upsert_request: UpsertForecastRequest,
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
) -> NoDataResponse:
    forecast_uc.upsert_forecast(request, upsert_request)
    return NoDataResponse(message="Success upserting forecast")
