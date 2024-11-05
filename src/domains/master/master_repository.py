# -*- coding: utf-8 -*-
from typing import List

from src.domains.master.entities.va_dealer import Dealer
from src.domains.master.entities.va_model import Model
from src.domains.master.master_interface import IMasterRepository
from sqlalchemy.orm import Session
from fastapi import Depends, Request
from src.dependencies.database_dependency import get_va_db
from src.models.responses.basic_response import TextValueResponse


class MasterRepository(IMasterRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return request.state.va_db if request.state.va_db is not None else self.va_db

    def first_or_create_dealer(self, request: Request, name: str) -> Dealer:
        dealer = (
            self.get_va_db(request)
            .query(Dealer)
            .filter(Dealer.name == name, Dealer.deletable == 0)
            .first()
        )
        if dealer is not None:
            return dealer
        else:
            dealer = Dealer(
                name=name,
            )

            self.get_va_db(request).add(dealer)
            self.get_va_db(request).flush()
            return dealer

    def find_model(self, request: Request, name: str | None = None) -> Model | None:
        query = self.get_va_db(request).query(Model).filter(Model.deletable == 0)

        if name is not None:
            query = query.filter(Model.name == name)

        return query.first()
