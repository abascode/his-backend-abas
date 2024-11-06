from datetime import datetime

from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text, event

from src.shared.utils.xid import generate_xid


class Dealer(BaseModel):
    __tablename__ = "va_dealers"

    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    name: MappedColumn[str] = mapped_column(String(255), nullable=False)
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))


@event.listens_for(Dealer, "before_insert")
def before_insert(mapper, connection, target: Dealer):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(Dealer, "before_update")
def before_update(mapper, connection, target: Dealer):
    target.updated_at = datetime.now()
