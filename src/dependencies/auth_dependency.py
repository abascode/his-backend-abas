import http

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request

from src.domains.users.user_interface import IUserRepository
from src.domains.users.user_repository import UserRepository

http_bearer = HTTPBearer()


def bearer_auth(
    request: Request,
    auth: HTTPAuthorizationCredentials = Security(http_bearer),
    user_repo: IUserRepository = Depends(UserRepository),
):
    user = user_repo.get_auth_user(request, auth.credentials.removeprefix("Bearer "))
    if user is None:
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED, detail="Unauthorized"
        )

    request.state.access_token = auth.credentials.removeprefix("Bearer ")
    request.state.user = user
