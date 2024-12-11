from typing import List

from pydantic import BaseModel

from src.models.responses.basic_response import TextValueResponse


class AllocationTargetMonthCategoryResponse(BaseModel):
    category: TextValueResponse
    target: int
    percentage: int  # persen dari total yang lain
    alloc_prev_month: int  # jumlah soa + oc
    ws: int  # db.total_ws
    total_alloc: int  # sum
    vs_target: int  # total_alloc / monthly_target * 100%
    vs_forecast: int  # total_alloc / ws * 100%


class AllocationTargetMonthResponse(BaseModel):
    month: int
    categories: List[AllocationTargetMonthCategoryResponse]


class AllocationAdjustmentMonthResponse(BaseModel):
    month: int
    adjustment: int
    ws: int  # db.total_ws
    ws_percentage: int  # ws / sum(ws) group by model
    allocation: int  # ((take off - bo) * stockpilot percent - (soa + oc + booking_prospect)) * forecast_order_percentage * ws_percentage
    confirmed_total_ws: int


class AllocationAdjustmentResponse(BaseModel):
    model: TextValueResponse
    category: TextValueResponse
    months: List[AllocationAdjustmentMonthResponse]


class GetAllocationResponse(BaseModel):
    dealer: TextValueResponse
    adjustments: List[AllocationAdjustmentResponse]
    monthly_targets: List[AllocationTargetMonthResponse]
