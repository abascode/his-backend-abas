

from typing import List
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse

from src.domains.calculation.calculation_interface import ICalculationUseCase
from src.domains.calculation.calculation_usecase import CalculationUseCase
from src.models.requests.calculation_request import CalculationTemplateRequest


router = APIRouter(prefix="/api/calculations", tags=["Calculations"])


@router.get("/template", response_class=FileResponse, summary="Get Calculation Template", description="This endpoint returns a calculation template in Excel format.")
def get_calculation_template(
   request: Request,
   query_params: CalculationTemplateRequest = Depends(),
   calculation_uc: ICalculationUseCase = Depends(CalculationUseCase),
   
):
    data =  calculation_uc.generate_calculation_excel_template(request, query_params)
    return FileResponse(
       path=data,
       media_type="application/vnd.ms-excel",
       filename="calculation_template.xlsx"
    )