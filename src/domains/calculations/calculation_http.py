import math

from fastapi import APIRouter, Depends, Form, UploadFile
from starlette.requests import Request

from src.domains.calculations.calculation_interface import ICalculationUseCase
from src.domains.calculations.calculation_usecase import CalculationUseCase
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

router = APIRouter(prefix="/api/calculations", tags=["Calculations"])


@router.post(
    "/take-off",
    response_model=NoDataResponse,
    summary="Upsert slot calculation take off data",
    description="Upsert slot calculation take off data",
)
def upsert_take_off_data(
    request: Request,
    take_off_data: UploadFile,
    month: int = Form(...),
    year: int = Form(...),
    calculation_uc: ICalculationUseCase = Depends(CalculationUseCase),
) -> NoDataResponse:
    calculation_uc.upsert_take_off_data(request, take_off_data, month, year)

    return NoDataResponse(message="Success uploading take off data!")
