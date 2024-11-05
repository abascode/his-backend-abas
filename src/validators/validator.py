import http
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.dependencies.database_dependency import get_sample_db
from src.validators.lang import en


class Validator:
    def __init__(self, data: Any, session: Session = next(get_sample_db())):
        self.data = data
        self.messages = {"en": en.messages}
        self.session: Session = session

    def unique_db(
        self,
        key: str,
        data_class: Any,
        attribute: str,
        neglect_attribute: str | None = None,
        *conditions: Any
    ) -> bool:
        query = self.session.query(data_class).filter(
            getattr(data_class, attribute) == getattr(self.data, key)
        )

        if neglect_attribute is not None:
            query = query.filter(
                getattr(data_class, neglect_attribute)
                != getattr(self.data, neglect_attribute)
            )

        for i in range(0, len(conditions), 2):
            value = conditions[i + 1] if conditions[i + 1] != "NULL" else None
            query = query.filter(getattr(data_class, conditions[i]) == value)

        if query.count() > 0:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=self.messages["en"]["unique"].format(key),
            )
        return True

    def exists(
        self, key: str, data_class: Any, attribute: str, *conditions: Any
    ) -> bool:
        query = self.session.query(data_class).filter(
            getattr(data_class, attribute) == getattr(self.data, key)
        )

        for i in range(0, len(conditions), 2):
            value = conditions[i + 1] if conditions[i + 1] != "NULL" else None
            query = query.filter(getattr(data_class, conditions[i]) == value)

        if query.count() == 0:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=self.messages["en"]["exists"].format(key),
            )

        return True
