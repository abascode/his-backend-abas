from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.domains.forecasts.forecast_interface import IForecastUseCase
from src.domains.forecasts.forecast_usecase import ForecastUseCase
from src.models.requests.forecast_request import CreateForecastRequest
from src.models.responses.basic_response import BasicResponse, NoDataResponse

router = APIRouter(prefix="/api/forecasts", tags=["Forecast"])


@router.post(
    "",
    response_model=NoDataResponse,
    summary="Upsert Forecast",
    description="Upsert forecast",
)
def upsert_forecast(
    request: Request,
    upsert_forecast_request: CreateForecastRequest,
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
) -> NoDataResponse:
    forecast_uc.create_forecast(request, upsert_forecast_request)

    return NoDataResponse(message="Success Upserting Forecast")
