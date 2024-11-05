from typing import TypeVar, Generic, List

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class IntegerIdResponse(BaseModel):
    id: int


class StringIdResponse(BaseModel):
    id: str


class BasicResponse(BaseModel, Generic[T]):
    data: T
    error: str | None = None
    message: str


# NOTE: this is strictly used for list of data, if the basic response can be used on list
#       this will be removed
class ListResponse(BaseModel, Generic[T]):
    data: List[T]
    error: str | None = None
    message: str


class NoDataResponse(BaseModel, Generic[T]):
    message: str


class PaginationMetadata(BaseModel):
    page: int
    size: int
    total_count: int
    page_count: int


class PaginationResponse(BaseModel, Generic[T]):
    data: List[T]
    metadata: PaginationMetadata
    message: str


class TextValueResponse(BaseModel):
    text: str
    value: str | int
