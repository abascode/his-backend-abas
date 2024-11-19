import abc
from typing import List

from starlette.requests import Request

from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_models import Model
from src.models.responses.basic_response import TextValueResponse


class IMasterUseCase:

    @abc.abstractmethod
    def get_dealer_options(self, request:Request, search: str | None = None
    ) -> List[TextValueResponse]:
        pass



class IMasterRepository:
    @abc.abstractmethod
    def find_model(self, request: Request, model_id: str) -> Model | None:
        pass

    @abc.abstractmethod
    def upsert_dealer(self, request: Request, dealer: Dealer) -> Dealer | None:
        pass

    @abc.abstractmethod
    def get_dealer_options(self, request: Request, search: str | None = None) -> List[Dealer]:
        pass
