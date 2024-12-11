from typing import List

from fastapi import Depends
from starlette.requests import Request

from src.domains.allocations.allocation_interface import (
    IAllocationRepository,
    IAllocationUseCase,
)
from src.domains.allocations.allocation_repository import AllocationRepository
from src.models.requests.allocation_request import GetAllocationRequest
from src.models.responses.allocation_response import (
    GetAllocationResponse,
    AllocationAdjustmentMonthResponse,
    AllocationAdjustmentResponse,
)
from src.models.responses.basic_response import TextValueResponse


class AllocationUseCase(IAllocationUseCase):

    def __init__(
        self,
        allocation_repo: IAllocationRepository = Depends(AllocationRepository),
    ):
        self.allocation_repo = allocation_repo

    def get_allocations(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ) -> List[GetAllocationResponse]:
        res = self.allocation_repo.get_allocation_adjustments(
            request, get_allocation_request
        )

        dealer_map = {}
        models_map = {}
        dealer_names = {}

        dealer_map = {}
        for i in res:
            (
                dealer_id,
                dealer,
                year,
                month,
                model_id,
                segment_id,
                category_id,
                forecast_month,
                adjustment,
                ws,
                ws_percentage,
                unfinished_allocation,
                allocation,
                confirmed_total_ws,
            ) = i

            if dealer_id not in dealer_map:
                dealer_map[dealer_id] = {}

            dealer_names[dealer_id] = dealer

            if model_id not in dealer_map[dealer_id]:
                dealer_map[dealer_id][model_id] = {}

            if model_id not in models_map:
                models_map[model_id] = {
                    "segment_id": segment_id,
                    "category_id": category_id,
                }

            dealer_map[dealer_id][model_id][forecast_month] = (
                AllocationAdjustmentMonthResponse(
                    month=forecast_month,
                    adjustment=adjustment,
                    ws=ws,
                    ws_percentage=ws_percentage,
                    allocation=allocation,
                    confirmed_total_ws=confirmed_total_ws,
                )
            )

        # class AllocationAdjustmentMonthResponse(BaseModel):
        #     month: int
        #     adjustment: int
        #     ws: int  # db.total_ws
        #     ws_percentage: int  # ws / sum(ws) group by model
        #     allocation: int  # ((take off - bo) * stockpilot percent - (soa + oc + booking_prospect)) * forecast_order_percentage * ws_percentage
        #     confirmed_total_ws: int
        #
        # class AllocationAdjustmentResponse(BaseModel):
        #     model: TextValueResponse
        #     category: TextValueResponse
        #     months: List[AllocationAdjustmentMonthResponse]
        #
        # class GetAllocationResponse(BaseModel):
        #     dealer: TextValueResponse
        #     adjustments: List[AllocationAdjustmentResponse]
        #     monthly_targets: List[AllocationTargetMonthResponse]

        allocations = []

        for dealer_id, dealer in dealer_names.items():
            adjustments = []

            for model_id, forecast_month_map in dealer_map[dealer_id].items():

                adjustment = AllocationAdjustmentResponse(
                    model=TextValueResponse(text=model_id, value=model_id),
                    category=TextValueResponse(
                        text=models_map[model_id]["category_id"],
                        value=models_map[model_id]["category_id"],
                    ),
                    months=[],
                )

                for forecast_month, month in forecast_month_map.items():
                    adjustment.months.append(month)

                adjustments.append(adjustment)

            allocations.append(
                GetAllocationResponse(
                    dealer=TextValueResponse(text=dealer, value=dealer_id),
                    adjustments=adjustments,
                    monthly_targets=[],
                )
            )
        return allocations
