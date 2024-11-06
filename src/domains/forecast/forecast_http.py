from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.domains.forecast.forecast_interface import IForecastUseCase
from src.domains.forecast.forecast_usecase import ForecastUseCase
from src.models.requests.forecast_request import UpsertForecastRequest
from src.models.responses.auth_response import LoginResponse
from src.models.responses.basic_response import (
    NoDataResponse,
    PaginationResponse,
    PaginationMetadata,
)
from src.dependencies.auth_dependency import bearer_auth

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

@router.get(
    "/api/forecasts/summaries",
    dependencies=[Depends(bearer_auth)],
    summary="Get Forecast Summary",
    description="Fetches a paginated list of Forecast based on the provided query parameters. Requires bearer token authentication.",
)
def get_forecast_summary(
    request: Request,
    query: ForecastSummaryRequest = Depends(),
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
):
    res, count = forecast_usecase.get_forecast_summary(request, query)
    return PaginationResponse(
        data=res,
        metadata=PaginationMetadata(
            page=query.page,
            size=query.size,
            total_count=count,
            page_count=math.ceil(count / query.size),
        ),
        total_data=count,
    )