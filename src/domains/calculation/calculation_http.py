from typing import List
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse

from src.domains.calculation.calculation_interface import ICalculationUseCase
from src.domains.calculation.calculation_usecase import CalculationUseCase
from src.models.requests.calculation_request import (
    CalculationTemplateRequest,
    GetCalculationDetailRequest,
)
from src.models.responses.basic_response import BasicResponse
from src.models.responses.calculation_response import CalculationDetailResponse

router = APIRouter(prefix="/api/calculations", tags=["Calculations"])


@router.get(
    "/template",
    response_class=FileResponse,
    summary="Get Calculation Template",
    description="This endpoint returns a calculation template in Excel format.",
)
def get_calculation_template(
    request: Request,
    query_params: CalculationTemplateRequest = Depends(),
    calculation_uc: ICalculationUseCase = Depends(CalculationUseCase),
):
    data = calculation_uc.generate_calculation_excel_template(request, query_params)
    return FileResponse(
        path=data,
        media_type="application/vnd.ms-excel",
        filename="calculation_template.xlsx",
    )


@router.get(
    "",
    response_model=BasicResponse[CalculationDetailResponse],
    description="Get calculation Detail",
    summary="Get Calculation Detail",
)
def get_calculation_detail(
    request: Request,
    get_calculation_detail_request: GetCalculationDetailRequest = Depends(),
    calculation_uc: ICalculationUseCase = Depends(CalculationUseCase),
) -> BasicResponse[CalculationDetailResponse]:
    data = calculation_uc.get_calculation_detail(
        request, get_calculation_detail_request
    )
    return BasicResponse(data=data)
