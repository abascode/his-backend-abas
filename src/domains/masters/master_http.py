from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.domains.masters.master_interface import IMasterUseCase
from src.domains.masters.master_usecase import MasterUseCase
from src.models.requests.master_request import GetOrderConfigurationRequest, GetStockPilotRequest
from src.models.responses.basic_response import TextValueResponse,ListResponse
from src.models.responses.master_response import OrderConfigurationsResponse, StockPilotsResponse

router = APIRouter(prefix="/api/master", tags=["Master"])

@router.get(
    "/dealers/options",
    response_model= ListResponse[TextValueResponse],
    summary="Dealer Options",
    description="Dealer Options",
)
def get_dealer_options(
    request: Request,
    search: str | None = "",
    dealer_uc: IMasterUseCase = Depends(MasterUseCase),
)->ListResponse[TextValueResponse]:
    dealers = dealer_uc.get_dealer_options(request,search)
    return ListResponse(data=dealers, message="Success Fetching Dealer Options")

@router.get(
    "/models/options",
    response_model= ListResponse[TextValueResponse],
    summary="Model Options",
    description="Model Options",
)
def get_model_options(
    request: Request,
    search: str | None = "",
    model_uc: IMasterUseCase = Depends(MasterUseCase),
)->ListResponse[TextValueResponse]:
    models = model_uc.get_model_options(request,search)
    return ListResponse(data=models, message="Success Fetching Model Options")


class OrderApprovalMatrixResponse:
    pass


@router.get(
    "/order-configuration",
    response_model= ListResponse[OrderConfigurationsResponse],
    summary="Order Configuration",
    description="Order Configuration",
)
def get_order_configuration(
    request: Request,
    order_configuration_request:GetOrderConfigurationRequest=Depends(),
    order_config_uc: IMasterUseCase = Depends(MasterUseCase),
)->ListResponse[OrderConfigurationsResponse]:
    orders = order_config_uc.get_order_configuration(request,order_configuration_request)
    return ListResponse(data=orders, message="Success Fetching Orders Configuration")

@router.get(
    "/stock-pilots",
    response_model= ListResponse[StockPilotsResponse],
    summary="Stock Pilot",
    description="Stock Pilot",
)
def get_stock_pilots(
    request: Request,
    stock_pilots_request:GetStockPilotRequest=Depends(),
    order_config_uc: IMasterUseCase = Depends(MasterUseCase),
)->ListResponse[StockPilotsResponse]:
    stock_pilots = order_config_uc.get_order_configuration(request,stock_pilots_request)
    return ListResponse(data=stock_pilots, message="Success Fetching Orders Configuration")

