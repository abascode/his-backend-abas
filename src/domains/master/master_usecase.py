from src.domains.master.master_interface import IMasterUseCase, IMasterRepository
from src.domains.master.master_repository import MasterRepository
from fastapi import Depends


class MasterUseCase(IMasterUseCase):
    def __init__(
        self,
        master_repository: IMasterRepository = Depends(MasterRepository),
    ):
        self.master_repository = master_repository
