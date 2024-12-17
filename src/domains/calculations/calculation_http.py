import http
import math

from fastapi import APIRouter, Depends, Form, UploadFile, HTTPException
from starlette.requests import Request

from src.domains.calculations.calculation_interface import ICalculationUseCase
from src.domains.calculations.calculation_usecase import CalculationUseCase
from src.domains.forecasts.forecast_interface import IForecastUseCase
from src.domains.forecasts.forecast_usecase import ForecastUseCase
from src.models.requests.calculation_request import GetCalculationRequest
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
from src.models.responses.calculation_response import GetCalculationResponse
from src.models.responses.forecast_response import GetForecastSummaryResponse
from src.shared.utils.storage_utils import save_file

router = APIRouter(prefix="/api/calculations", tags=["Calculations"])


@router.post(
    "/take-off",
    response_model=NoDataResponse,
    summary="Upsert slot calculation take off data",
    description="Upsert slot calculation take off data",
)
def upsert_take_off_data(
    request: Request,
    file: UploadFile,
    month: int = Form(...),
    year: int = Form(...),
    calculation_uc: ICalculationUseCase = Depends(CalculationUseCase),
) -> NoDataResponse:
    calculation_uc.upsert_take_off_data(request, file, month, year)

    return NoDataResponse(message="Success uploading take off data!")


@router.post(
    # temporary
    "/booking",
    response_model=NoDataResponse,
    summary="Upsert slot calculation SOA, BO",
    description="Upsert slot calculation take off data",
)
def upsert_soa_bo_oc_booking_data(
    request: Request,
    file: UploadFile,
    month: int = Form(...),
    year: int = Form(...),
    calculation_uc: ICalculationUseCase = Depends(CalculationUseCase),
) -> NoDataResponse:
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail="Please upload excel file",
        )

    path = save_file("calculations", file)
    calculation_uc.upsert_bo_soa_oc_booking_prospect(request, path, month, year)
    return NoDataResponse(message="Success uploading SOA, SO, BO, OC, Booking data")


@router.get(
    "",
    response_model=BasicResponse[GetCalculationResponse],
    summary="Get calculation detail",
    description="Get calculation details",
)
def get_calculation_detail(
    request: Request,
    get_calculation_request: GetCalculationRequest = Depends(),
    calculation_uc: ICalculationUseCase = Depends(CalculationUseCase),
) -> BasicResponse[GetCalculationRequest]:
    data = calculation_uc.get_calculation_detail(request, get_calculation_request)

    return BasicResponse(data=data, message="Success getting calculation detail")
