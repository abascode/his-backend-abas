import math

from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.domains.forecasts.forecast_interface import IForecastUseCase
from src.domains.forecasts.forecast_usecase import ForecastUseCase
from src.models.requests.forecast_request import (
    CreateForecastRequest,
    GetForecastSummaryRequest,
    GetForecastDetailRequest,
)
from src.models.responses.basic_response import (
    BasicResponse,
    NoDataResponse,
    PaginationResponse,
    PaginationMetadata,
)
from src.models.responses.forecast_response import GetForecastSummaryResponse

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
    forecast_uc.upsert_forecast(request, upsert_forecast_request)

    return NoDataResponse(message="Success Upserting Forecast")


@router.get(
    "/summaries",
    response_model=PaginationResponse[GetForecastSummaryResponse],
    summary="Get Forecast Summaries",
    description="Get Forecast Summaries",
)
def get_forecast_summaries(
    request: Request,
    query: GetForecastSummaryRequest = Depends(),
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
) -> PaginationResponse[GetForecastSummaryResponse]:
    res, cnt = forecast_uc.get_forecast_summary(request, query)

    return PaginationResponse(
        data=res,
        metadata=PaginationMetadata(
            page=query.page,
            size=query.size,
            total_count=cnt,
            page_count=math.ceil(cnt / query.size),
        ),
        message="Success getting summaries",
    )


@router.get("")
def get_forecast_detail(
    request: Request,
    get_forecast_detail_request: GetForecastDetailRequest = Depends(),
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
):
    res = forecast_uc.get_forecast_detail(request, get_forecast_detail_request)

    return BasicResponse(data=res, message="Success getting forecast detail")
