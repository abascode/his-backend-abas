from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class DatabaseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.va_db = None
        response = await call_next(request)
        return response
