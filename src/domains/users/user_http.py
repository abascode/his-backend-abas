import http
from fastapi import APIRouter, Depends, HTTPException, Request

from src.dependencies.auth_dependency import bearer_auth
from src.domains.users.user_interface import IUserRepository
from src.domains.users.user_repository import UserRepository
from src.models.requests.auth_request import LoginRequest

from src.models.responses.auth_response import LoginResponse


router = APIRouter(prefix="/api/auth", tags=["Auth (Dev Only)"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login",
    description="This endpoint allows a user to log in by providing their email and password. It returns a `LoginResponse` model on success, or a `401 Unauthorized` error if the credentials are invalid.",
)
def login(
    request: Request,
    login_request: LoginRequest,
    user_repo: IUserRepository = Depends(UserRepository),
) -> LoginResponse:
    res = user_repo.login(request, login_request.email, login_request.password)
    if res is None:
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED, detail="Unauthorized"
        )
    return res


@router.get(
    "/me",
    summary="Get Authenticated User",
    description="This endpoint returns the currently authenticated user's information.",
)
def get_auth_user(
    request: Request,
):
    return request.state.user
