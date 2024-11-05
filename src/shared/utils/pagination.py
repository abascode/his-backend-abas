from typing import TypeVar

from sqlalchemy.orm import Query

T = TypeVar("T")


def paginate(query: Query, page: int, size: int) -> tuple[list[T], int]:
    total_count = query.count()
    offset = (page - 1) * size
    results = query.limit(size).offset(offset).all()
    return results, total_count
