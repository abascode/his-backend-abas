from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.domains.allocations.enums import AllocationApprovalFlagEnum
from src.models.responses.basic_response import TextValueResponse


class AllocationTargetMonthMonthResponse(BaseModel):
    month: int
    target: int
    percentage: int  # persen dari total yang lain
    alloc_prev_month: int  # jumlah soa + oc
    ws: int  # db.total_ws
    total_alloc: int  # sum
    vs_target: int  # total_alloc / monthly_target * 100%
    vs_forecast: int  # total_alloc / ws * 100%


class AllocationTargetMonthCategoryResponse(BaseModel):
    category: TextValueResponse
    months: List[AllocationTargetMonthMonthResponse]


class AllocationTargetMonthResponse(BaseModel):
    dealer: TextValueResponse
    categories: List[AllocationTargetMonthCategoryResponse]


class AllocationAdjustmentMonthResponse(BaseModel):
    id: str
    month: int
    adjustment: int
    ws: int  # db.total_ws
    ws_percentage: int  # ws / sum(ws) group by model
    allocation: int  # ((take off - bo) * stockpilot percent - (soa + oc + booking_prospect)) * forecast_order_percentage * ws_percentage
    confirmed_total_ws: int


class AllocationAdjustmentModelResponse(BaseModel):
    model: TextValueResponse
    segment: TextValueResponse
    category: TextValueResponse
    remaining_stock: int
    months: List[AllocationAdjustmentMonthResponse]


class GetAllocationAdjustmentResponse(BaseModel):
    dealer: TextValueResponse
    models: List[AllocationAdjustmentModelResponse]


class AllocationApprovalResponse(BaseModel):
    id: str
    approver: TextValueResponse | None
    approved_at: datetime | None
    approved_comment: str | None
    approval_flag: AllocationApprovalFlagEnum
    role: TextValueResponse


class GetAllocationResponse(BaseModel):
    approvals: List[AllocationApprovalResponse]
    adjustments: List[GetAllocationAdjustmentResponse]
    targets: List[AllocationTargetMonthResponse]
