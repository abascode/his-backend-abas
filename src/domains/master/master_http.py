# -*- coding: utf-8 -*-
from typing import List
from fastapi import APIRouter, Request, Depends
from src.dependencies.auth_dependency import bearer_auth
from src.models.responses.basic_response import TextValueResponse
from src.domains.master.master_interface import IMasterUseCase
from src.domains.master.master_usecase import MasterUseCase
from src.models.responses.basic_response import ListResponse

router = APIRouter(prefix="/api/master", tags=["Vehicle Allocation Master"])
