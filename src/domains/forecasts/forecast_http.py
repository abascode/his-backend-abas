import math

from fastapi import APIRouter, Depends, File, Form, UploadFile
from starlette.requests import Request

from src.dependencies.auth_dependency import api_key_auth
from src.domains.forecasts.forecast_interface import IForecastUseCase
from src.domains.forecasts.forecast_usecase import ForecastUseCase
from src.models.requests.allocation_request import GetAllocationRequest
from src.models.requests.forecast_request import (
    CreateForecastRequest,
    GetForecastSummaryRequest,
    GetForecastDetailRequest,
    ConfirmForecastRequest,
    ApprovalAllocationRequest,
)
from src.models.responses.basic_response import (
    BasicResponse,
    NoDataResponse,
    PaginationResponse,
    PaginationMetadata,
    PdfResponse,
)
from src.models.responses.forecast_response import GetForecastSummaryResponse

router = APIRouter(prefix="/api/forecasts", tags=["Forecast"])


@router.post(
    "",
    response_model=NoDataResponse,
    summary="Upsert Forecast",
    description="Upsert forecast",
    # dependencies=[Depends(api_key_auth)],
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


@router.post(
    "/confirm", dependencies=[Depends(api_key_auth)], response_model=PdfResponse
)
def confirm_forecast(
    request: Request,
    confirm_request: ConfirmForecastRequest,
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
):
    forecast_uc.confirm_forecast(request, confirm_request)

    return PdfResponse(
        message="Success confirming forecast", document_link="https://www.google.com"
    )


@router.get(
    "/pdf",
    dependencies=[Depends(api_key_auth)],
    summary="Generate Order Confirmation PDF",
)
def generate_forecast_pdf(
    request: Request,
    get_forecast_detail_request: GetForecastDetailRequest = Depends(),
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
):
    data = forecast_uc.generate_forecast_pdf(request, get_forecast_detail_request)
    return data
