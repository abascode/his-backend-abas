from typing import List
from fastapi import APIRouter, Request, Depends
from src.models.requests.master_request import StockPilotRequest
from src.models.responses.basic_response import TextValueResponse, BasicResponse
from src.domains.master.master_interface import IMasterUseCase
from src.domains.master.master_usecase import MasterUseCase
from src.models.responses.basic_response import ListResponse
from src.models.responses.forecast_response import DealerForecastResponse
from src.models.responses.master_response import StockPilotResponse

router = APIRouter(prefix="/api/master", tags=["Vehicle Allocation Master"])


@router.get("/stock-pilots", response_model=BasicResponse[List[StockPilotResponse]])
def get_stock_pilots(
    request: Request,
    get_stock_pilot_request: StockPilotRequest = Depends(),
    master_usecase: IMasterUseCase = Depends(MasterUseCase),
) -> BasicResponse[List[StockPilotResponse]]:
    data = master_usecase.get_stock_pilots(request, get_stock_pilot_request)
    return BasicResponse(data=data)


@router.get(
    "/dealers/options",
    # dependencies=[Depends(bearer_auth)],
    response_model=ListResponse[TextValueResponse],
    summary="Get Dealer Options",
    description="Fetches a list of dealer options based on an optional search parameter. Requires bearer token authentication.",
)
def get_dealer_options(
    request: Request,
    search: str | None = "",
    dealer_usecase: IMasterUseCase = Depends(MasterUseCase),
) -> ListResponse[TextValueResponse]:
    res = dealer_usecase.get_dealer_options(request, search)
    return ListResponse(data=res, message="Success getting dealer options")


@router.get(
    "/forecast-orders",
    dependencies=[],
    response_model=ListResponse[ForecastOrderResponse],
    summary="Get Forecast Orders",
    description="Fetches a list of Forecast Orders. Requires bearer token authentication.",
)
def get_forecast_orders(
    request: Request, forecast_usecase: IMasterUseCase = Depends(MasterUseCase)
) -> ListResponse[ForecastOrderResponse]:
    res = forecast_usecase.get_forecast_order(request)
    return ListResponse(data=res, message="Success getting forecast orders")


@router.get(
    "/urgent-orders",
    dependencies=[],
    response_model=ListResponse[ForecastOrderResponse],
    summary="Get Urgent Orders",
    description="Fetches a list of Urgent Orders. Requires bearer token authentication.",
)
def get_urgent_orders(
    request: Request, forecast_usecase: IMasterUseCase = Depends(MasterUseCase)
) -> ListResponse[ForecastOrderResponse]:
    res = forecast_usecase.get_urgent_orders(request)
    return ListResponse(data=res, message="Success getting urgent orders")
