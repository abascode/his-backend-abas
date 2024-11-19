import abc

from starlette.requests import Request

from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_models import Model


class IMasterRepository:
    @abc.abstractmethod
    def find_model(self, request: Request, model_id: str) -> Model | None:
        pass

    @abc.abstractmethod
    def upsert_dealer(self, request: Request, dealer: Dealer) -> Dealer | None:
        pass
