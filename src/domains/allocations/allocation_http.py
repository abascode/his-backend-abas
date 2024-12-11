import math

from fastapi import APIRouter, Depends, File, Form, UploadFile
from starlette.requests import Request

from src.dependencies.auth_dependency import api_key_auth
from src.domains.allocations.allocation_interface import IAllocationUseCase
from src.domains.allocations.allocation_usecase import AllocationUseCase
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
from src.models.responses.allocation_response import GetAllocationResponse
from src.models.responses.basic_response import (
    BasicResponse,
    ListResponse,
)

router = APIRouter(prefix="/api/allocations", tags=["Allocation"])


@router.get("", response_model=ListResponse[GetAllocationResponse])
def get_allocation_detail(
    request: Request,
    get_allocation_request: GetAllocationRequest = Depends(),
    allocation_uc: IAllocationUseCase = Depends(AllocationUseCase),
):
    res = allocation_uc.get_allocations(request, get_allocation_request)

    return ListResponse(data=res, message="Success getting forecast detail")
