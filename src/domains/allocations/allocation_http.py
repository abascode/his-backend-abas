import math

from fastapi import APIRouter, Depends, File, Form, UploadFile
from starlette.requests import Request

from src.dependencies.auth_dependency import api_key_auth, bearer_auth
from src.domains.allocations.allocation_interface import IAllocationUseCase
from src.domains.allocations.allocation_usecase import AllocationUseCase
from src.domains.forecasts.forecast_interface import IForecastUseCase
from src.domains.forecasts.forecast_usecase import ForecastUseCase
from src.models.requests.allocation_request import (
    GetAllocationRequest,
    SubmitAllocationRequest,
)
from src.models.requests.forecast_request import (
    CreateForecastRequest,
    GetForecastSummaryRequest,
    GetForecastDetailRequest,
    ConfirmForecastRequest,
    ApprovalAllocationRequest,
)
from src.models.responses.allocation_response import (
    GetAllocationAdjustmentResponse,
    GetAllocationResponse,
)
from src.models.responses.basic_response import (
    BasicResponse,
    ListResponse,
    NoDataResponse,
)

router = APIRouter(prefix="/api/allocations", tags=["Allocation"])


@router.post(
    "/approve",
    response_model=NoDataResponse,
    summary="Approve Allocation",
    description="Approve Allocation",
    # dependencies=[Depends(api_key_auth)],
)
def approve_allocation(
    request: Request,
    approval_request: ApprovalAllocationRequest,
    uc: IAllocationUseCase = Depends(AllocationUseCase),
) -> NoDataResponse:
    uc.approve_allocation(request, approval_request)

    return NoDataResponse(message="Success approving allocation data")


@router.post(
    "/monthly-target",
    response_model=NoDataResponse,
    summary="Upsert Monthly Target",
    description="Upsert Monthly Target",
)
def upsert_monthly_target(
    request: Request,
    file: UploadFile = File(...),
    month: int = Form(...),
    year: int = Form(...),
    forecast_uc: IForecastUseCase = Depends(ForecastUseCase),
) -> NoDataResponse:
    forecast_uc.upsert_monthly_target(request, file, month, year)

    return NoDataResponse(message="Success Upserting Monthly Target")


@router.get("", response_model=BasicResponse[GetAllocationResponse])
def get_allocation_detail(
    request: Request,
    get_allocation_request: GetAllocationRequest = Depends(),
    allocation_uc: IAllocationUseCase = Depends(AllocationUseCase),
):
    res = allocation_uc.get_allocations(request, get_allocation_request)

    return BasicResponse(data=res, message="Success getting allocation")


@router.post("", response_model=NoDataResponse, dependencies=[Depends(bearer_auth)])
def submit_allocation(
    request: Request,
    submit_allocation_request: SubmitAllocationRequest,
    allocation_uc: IAllocationUseCase = Depends(AllocationUseCase),
) -> NoDataResponse:
    allocation_uc.submit_allocation(request, submit_allocation_request)
    return NoDataResponse(message="Success submitting allocation")
