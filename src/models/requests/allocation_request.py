from pydantic import BaseModel

from src.domains.allocations.enums import AllocationSubmissionStatusEnum


class GetAllocationRequest(BaseModel):
    month: int
    year: int


class UpdateAllocationAdjustmentRequest(BaseModel):
    forecast_detail_id: str


class SubmitAllocationAdjustmentRequest(BaseModel):
    forecast_detail_month_id: str
    adjustment: int


class SubmitAllocationRequest(BaseModel):
    status: AllocationSubmissionStatusEnum
    month: int
    year: int
    adjustments: list[SubmitAllocationAdjustmentRequest]
