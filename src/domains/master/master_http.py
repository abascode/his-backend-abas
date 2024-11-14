from typing import List
from fastapi import APIRouter, Request, Depends
from src.models.requests.master_request import StockPilotRequest
from src.models.responses.basic_response import TextValueResponse, BasicResponse
from src.domains.master.master_interface import IMasterUseCase
from src.domains.master.master_usecase import MasterUseCase
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
