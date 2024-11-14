from typing import List
from src.domains.master.master_interface import IMasterUseCase, IMasterRepository
from src.domains.master.master_repository import MasterRepository
from fastapi import Depends, Request
from src.models.responses.basic_response import TextValueResponse


class MasterUseCase(IMasterUseCase):
    def __init__(
        self,
        master_repository: IMasterRepository = Depends(MasterRepository),
    ):
        self.master_repository = master_repository
        
    def get_dealer_options(
        self, request: Request, search: str | None = None
    ) -> List[TextValueResponse]:
        data = self.master_repository.get_dealer_options(request, search)

        return [
            TextValueResponse(
                text=i.name,
                value=i.id,
            )
            for i in data
        ]
