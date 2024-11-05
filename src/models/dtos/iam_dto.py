from datetime import datetime
from typing import List

from pydantic import BaseModel


class IamPermissionPivot(BaseModel):
    permission_id: int


class IamPermission(BaseModel):
    id: int
    name: str
    guard_name: str
    id_module: int
    pivot: IamPermissionPivot


class IamUserDto(BaseModel):
    id: int
    name: str
    username: str
    email: str
    last_login_at: str
    division_id: str | None
    department_id: str | None
    role_name: List[str]
