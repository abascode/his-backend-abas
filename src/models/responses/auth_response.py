from datetime import datetime

from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
