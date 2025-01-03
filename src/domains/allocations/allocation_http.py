import http
import math

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    HTTPException,
    BackgroundTasks,
)
from starlette.requests import Request
from starlette.responses import FileResponse

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
from src.shared.utils.storage_utils import save_file

router = APIRouter(prefix="/api/allocations", tags=["Allocation"])


@router.post(
    "/approve",
    summary="Approve Allocation",
    description="Approve Allocation",
    dependencies=[Depends(bearer_auth)],
)
def approve_allocation(
    request: Request,
    approval_request: ApprovalAllocationRequest,
    uc: IAllocationUseCase = Depends(AllocationUseCase),
):
    res = uc.approve_allocation(request, approval_request)
    return res
    return BasicResponse(data=res, message="Success approving allocation data")


@router.post("/send-to-hoyu", response_model=NoDataResponse)
def send_to_hoyu(
    request: Request,
    background_task: BackgroundTasks,
    approval_request: ApprovalAllocationRequest,
    uc: IAllocationUseCase = Depends(AllocationUseCase),
):
    background_task.add_task(uc.send_allocation_to_hoyu, request, approval_request)
    return NoDataResponse(message="Success sending allocation data to HOYU")


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
    allocation_uc: IAllocationUseCase = Depends(AllocationUseCase),
) -> NoDataResponse:
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail="Please upload excel file",
        )
    path = save_file("allocations", file)
    allocation_uc.upsert_monthly_target(request, path, month, year)

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


@router.get(
    "/template/monthly-target",
    summary="Download monthly target template",
    description="Download monthly target template",
)
def download_monthly_target_template(
    request: Request,
    month: int,
    year: int,
    allocation_uc: IAllocationUseCase = Depends(AllocationUseCase),
) -> FileResponse:
    path = allocation_uc.download_monthly_target_excel_template(request, month, year)
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename="{}-{}-allocation-monthly-target-template.xlsx".format(month, year),
    )
