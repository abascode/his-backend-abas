import abc
from typing import List

from fastapi import Request

from src.models.dtos.iam_dto import IamUserDto
from src.models.responses.auth_response import LoginResponse


class IUserRepository:
    @abc.abstractmethod
    def get_auth_user(self, request: Request, access_token: str) -> IamUserDto | None:
        pass

    @abc.abstractmethod
    def login(
        self, request: Request, email: str, password: str
    ) -> LoginResponse | None:
        pass
