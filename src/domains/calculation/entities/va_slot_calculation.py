
from datetime import datetime
from typing import List
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from sqlalchemy import DateTime, String, Integer, func, text,event

from src.shared.utils.xid import generate_xid


class SlotCalculation(BaseModel):
    __tablename__ = "va_slot_calculations"
    
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    month: MappedColumn[int] = mapped_column(Integer, nullable=False)
    year: MappedColumn[int] = mapped_column(Integer, nullable=False)
    forecast_order_cat_2: MappedColumn[int] = mapped_column(Integer, nullable=False)
    forecast_order_cat_3: MappedColumn[int] = mapped_column(Integer, nullable=False)
    urgent_order_cat_2: MappedColumn[int] = mapped_column(Integer, nullable=False)
    urgent_order_cat_3: MappedColumn[int] = mapped_column(Integer, nullable=False)
    
    created_by: MappedColumn[str] = mapped_column(
        String(255),
        nullable=True,
    )
    updated_by: MappedColumn[str] = mapped_column(
        String(255),
        nullable=True,
    )
    deleted_by: MappedColumn[str] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))
    
    # TODO do these need "calculations" prefix?
    stock_pilots: MappedColumn[List["SlotCalculationStockPilot"]] = relationship("SlotCalculationStockPilot", back_populates="slot_calculation") 
    models: MappedColumn[List["SlotCalculationModel"]] = relationship("SlotCalculationModel", back_populates="slot_calculation")
    
@event.listens_for(SlotCalculation, "before_insert")
def before_insert(mapper, connection, target: SlotCalculation):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(SlotCalculation, "before_update")
def before_update(mapper, connection, target: SlotCalculation):
    target.updated_at = datetime.now()