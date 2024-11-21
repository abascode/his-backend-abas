import http
import os
from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from apscheduler.schedulers.background import BackgroundScheduler

from src.dependencies.database_dependency import get_va_db
from src.domains.users.user_http import router as user_router
from src.domains.forecasts.forecast_http import router as forecast_router
from src.domains.calculations.calculation_http import router as calculation_router

from src.domains.masters.master_http import router as master_router
from src.shared.middlewares.database_middleware import DatabaseMiddleware
from src.shared.utils.database_utils import rollback_all

app = FastAPI(
    title="HIS Vehicle Allocation Backend",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DatabaseMiddleware)


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(
#     request: Request, exc: RequestValidationError
# ) -> JSONResponse:
#     rollback_all(request)
#     return JSONResponse(
#         status_code=http.HTTPStatus.BAD_REQUEST,
#         content=jsonable_encoder(
#             {
#                 "error": " ".join([str(i) for i in exc.errors()[0]["loc"]])
#                 + " "
#                 + exc.errors()[0]["msg"],
#                 "status_code": http.HTTPStatus.BAD_REQUEST,
#             }
#         ),
#     )


# @app.exception_handler(ValidationError)
# async def validation_exception_handler(
#     request: Request, exc: ValidationError
# ) -> JSONResponse:
#     rollback_all(request)
#     err = " ".join([str(i) for i in exc.errors()[0]["loc"]])
#     return JSONResponse(
#         status_code=http.HTTPStatus.BAD_REQUEST,
#         content=jsonable_encoder(
#             {
#                 "error": err + ": " + exc.errors()[0]["msg"],
#                 "status_code": http.HTTPStatus.BAD_REQUEST,
#             }
#         ),
#     )

#
# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(
#     request: Request, exc: StarletteHTTPException
# ) -> JSONResponse:
#     rollback_all(request)
#     return JSONResponse(
#         status_code=exc.status_code,
#         content=jsonable_encoder({"error": exc.detail, "status_code": exc.status_code}),
#     )
#
#
# @app.exception_handler(500)
# async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
#     rollback_all(request)
#     return JSONResponse(
#         status_code=500,
#         content=jsonable_encoder({"status_code": 500, "error": str(exc)}),
#     )


@app.get(
    "/",
    summary="Check API Status",
    description="This endpoint is used to check if the API is running and accessible.",
)
def root():
    return {"status": "200 OK"}


@app.get(
    "/api/status",
    summary="Get Application Version",
    description="This endpoint returns the current version of the application based on the `APP_VERSION` environment variable.",
)
def default():
    return {"version": os.getenv("APP_VERSION")}


app.include_router(user_router)
app.include_router(forecast_router)
app.include_router(calculation_router)
app.include_router(master_router)
