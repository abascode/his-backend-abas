from fastapi import APIRouter
from fastapi.params import Depends
from starlette.requests import Request

from src.domains.masters.master_interface import IMasterUseCase
from src.domains.masters.master_usecase import MasterUseCase
from src.models.responses.basic_response import TextValueResponse,ListResponse

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
    data = dealer_uc.get_dealer_options(request,search)
    return ListResponse(data=data, message="Success Fetching Dealer Options")