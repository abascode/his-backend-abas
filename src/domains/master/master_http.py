# -*- coding: utf-8 -*-
from typing import List
from fastapi import APIRouter, Request, Depends
from src.dependencies.auth_dependency import bearer_auth
from src.models.responses.basic_response import TextValueResponse
from src.domains.master.master_interface import IMasterUseCase
from src.domains.master.master_usecase import MasterUseCase
from src.models.responses.basic_response import ListResponse

router = APIRouter(prefix="/api/master", tags=["Vehicle Allocation Master"])

@router.get(
    "/dealers/options",
    dependencies=[Depends(bearer_auth)],
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
