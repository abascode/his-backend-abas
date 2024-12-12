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
    GetAllocationAdjustmentResponse,
    AllocationAdjustmentMonthResponse,
    AllocationAdjustmentModelResponse,
    AllocationTargetMonthCategoryResponse,
    GetAllocationResponse,
    AllocationTargetMonthMonthResponse,
    AllocationTargetMonthResponse,
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
    ) -> GetAllocationResponse:
        adjustment_data = self.allocation_repo.get_allocation_adjustments(
            request, get_allocation_request
        )
        monthly_target_data = self.allocation_repo.get_allocation_monthly_target(
            request, get_allocation_request
        )

        total_alloc_map = {}
        dealer_adjustment_map = {}
        model_map = {}
        dealer_map = {}

        for i in adjustment_data:
            (
                dealer_id,
                dealer,
                year,
                month,
                model_id,
                segment_id,
                category_id,
                forecast_month,
                adjustment_model,
                ws,
                ws_percentage,
                unfinished_allocation,
                allocation,
                confirmed_total_ws,
            ) = i

            if dealer_id not in dealer_map:
                dealer_map[dealer_id] = dealer

            if dealer_id not in dealer_adjustment_map:
                dealer_adjustment_map[dealer_id] = {}

            if model_id not in dealer_adjustment_map[dealer_id]:
                dealer_adjustment_map[dealer_id][model_id] = {}

            if dealer_id not in total_alloc_map:
                total_alloc_map[dealer_id] = {}

            if model_id not in model_map:
                model_map[model_id] = {
                    "segment_id": segment_id,
                    "category_id": category_id,
                }

            if category_id not in total_alloc_map[dealer_id]:
                total_alloc_map[dealer_id][category_id] = 0

            total_alloc_map[dealer_id][category_id] += allocation

            dealer_adjustment_map[dealer_id][model_id][forecast_month] = (
                AllocationAdjustmentMonthResponse(
                    month=forecast_month,
                    adjustment=adjustment_model,
                    ws=ws,
                    ws_percentage=ws_percentage,
                    allocation=allocation,
                    confirmed_total_ws=confirmed_total_ws,
                )
            )

        adjustments = []

        for dealer_id, dealer_adjustment_model in dealer_adjustment_map.items():
            adjustment = GetAllocationAdjustmentResponse(
                dealer=TextValueResponse(text=dealer_map[dealer_id], value=dealer_id),
                models=[],
            )

            for model_id, forecast_month_map in dealer_adjustment_map[
                dealer_id
            ].items():
                adjustment_model = AllocationAdjustmentModelResponse(
                    model=TextValueResponse(text=model_id, value=model_id),
                    category=TextValueResponse(
                        text=model_map[model_id]["category_id"],
                        value=model_map[model_id]["category_id"],
                    ),
                    months=[],
                )

                for forecast_month, month in forecast_month_map.items():
                    adjustment_model.months.append(month)

                adjustment.models.append(adjustment_model)
            adjustments.append(adjustment)

        monthly_target_map = {}
        category_target = {}

        for (
            category_id,
            target,
            dealer_id,
            forecast_month,
            alloc_prev_month,
            ws,
        ) in monthly_target_data:
            total_alloc = total_alloc_map.get(dealer_id, {}).get(category_id, 0)
            vs_target = int(total_alloc / (target * 100)) if target else 0
            vs_forecast = int(total_alloc / (ws * 100)) if ws else 0

            if dealer_id not in monthly_target_map:
                monthly_target_map[dealer_id] = {}

            if category_id not in monthly_target_map[dealer_id]:
                monthly_target_map[dealer_id][category_id] = []

            if forecast_month not in category_target:
                category_target[category_id] = 0

            category_target[category_id] += target

            monthly_target_map[dealer_id][category_id].append(
                AllocationTargetMonthMonthResponse(
                    month=forecast_month,
                    target=target,
                    percentage=0,
                    alloc_prev_month=alloc_prev_month,
                    ws=ws,
                    total_alloc=total_alloc,
                    vs_target=vs_target,
                    vs_forecast=vs_forecast,
                )
            )

        targets = []
        for dealer_id, category_map in monthly_target_map.items():
            target = AllocationTargetMonthResponse(
                dealer=TextValueResponse(
                    text=dealer_map.get(dealer_id, "-"), value=dealer_id
                ),
                categories=[],
            )

            percentage: int  # persen dari total yang lain

            for category_id, months in category_map.items():
                for i in months:
                    i.percentage = int(i.target / category_target[category_id] * 100)

                target.categories.append(
                    AllocationTargetMonthCategoryResponse(
                        category=TextValueResponse(text=category_id, value=category_id),
                        months=months,
                    )
                )

            targets.append(target)

        return GetAllocationResponse(adjustments=adjustments, targets=targets)
