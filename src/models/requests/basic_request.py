from pydantic import BaseModel
from src.shared.enums import TableOrderEnum


class TableRequest(BaseModel):
    page: int
    size: int
    order: TableOrderEnum = TableOrderEnum.asc
    order_by: str | None = None
