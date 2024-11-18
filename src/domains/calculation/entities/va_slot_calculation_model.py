
from datetime import datetime
from typing import List
from src.domains.calculation.entities.va_slot_calculation import SlotCalculation
from src.domains.master.entities.va_model import Model
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text, event

from src.shared.utils.xid import generate_xid


class SlotCalculationModel(BaseModel):
    __tablename__ = "va_slot_calculation_models"
    
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    slot_calculation_id: MappedColumn[str] = mapped_column(String (255), ForeignKey('va_slot_calculation.id'),nullable=False)
    model_id: MappedColumn[str] = mapped_column(String (255), ForeignKey('va_models.id'),nullable=False)
   
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
    
    slot_calculation: MappedColumn[SlotCalculation] = relationship("SlotCalculation")
    model: MappedColumn[Model] = relationship(Model)  
    months: MappedColumn[List["SlotCalculationMonth"]] = relationship("SlotCalculationMonth", back_populates="slot_calculation_model")
    
    
@event.listens_for(SlotCalculationModel, "before_insert")
def before_insert(mapper, connection, target: SlotCalculationModel):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(SlotCalculationModel, "before_update")
def before_update(mapper, connection, target: SlotCalculationModel):
    target.updated_at = datetime.now()