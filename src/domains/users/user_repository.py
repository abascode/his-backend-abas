import http
from typing import List

import requests
from starlette.requests import Request
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from src.config.config import get_config
from src.dependencies.database_dependency import get_va_db
from src.domains.users.user_interface import IUserRepository
from src.models.dtos.iam_dto import IamUserDto
from src.models.responses.auth_response import LoginResponse


class UserRepository(IUserRepository):

    def __init__(self, get_va_db: Session = Depends(get_va_db)):
        self.get_va_db = get_va_db

    def get_va_db(self, request: Request) -> Session:
        return (
            request.state.va_db if request.state.va_db is not None else self.get_va_db
        )

    def login(
        self, request: Request, email: str, password: str
    ) -> LoginResponse | None:
        try:
            url = get_config().outbound["iam"].base_url + "/v1/login"
            response = requests.post(
                url, json={"email": email, "password": password}, timeout=10
            )

            if response.status_code != 200:
                return None
            else:
                return LoginResponse(**response.json())
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Outbound Timeout: iam/v1/login",
            )

    def get_auth_user(self, request: Request, access_token: str) -> IamUserDto | None:
        try:
            url = get_config().outbound["iam"].base_url + "/v1/verify-user"

            response = requests.post(
                url,
                headers={"Authorization": "Bearer {}".format(access_token)},
                timeout=10,
            )

            if response.status_code != 200:
                return None

            data = response.json()

            if len(data["rolesdivision"]) == 0:
                return None

            return IamUserDto(
                id=data["id"],
                name=data["name"],
                username=data["username"],
                email=data["email"],
                last_login_at=data["last_login_at"],
                division_id=data["division_id"],
                department_id=data["department_id"],
                role_name=data["role_name"],
            )
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Outbound Timeout: iam/v1/verify-user",
            )
