from typing import Optional

from sqlalchemy.orm import mapped_column, relationship, declared_attr
from sqlalchemy import String, ForeignKey, Integer
from src.shared.entities.basemodel import BaseModel


class User(BaseModel):
    __tablename__ = "va_users"
    __allow_unmapped__ = True
    id = mapped_column(String(255), nullable=False, primary_key=True)
    name = mapped_column(String(255), nullable=False)
    role_id = mapped_column(Integer, nullable=True)
    email = mapped_column(String(255), nullable=False, server_default="-")
