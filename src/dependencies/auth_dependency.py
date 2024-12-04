import http

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader
from starlette.requests import Request

from src.config.config import get_config
from src.domains.users.user_interface import IUserRepository
from src.domains.users.user_repository import UserRepository

http_bearer = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key")


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


def api_key_auth(request: Request, api_key_header: str = Security(api_key_header)):
    print(get_config().app.api_keys)
    if api_key_header not in get_config().app.api_keys:
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED, detail="Unauthorized"
        )
