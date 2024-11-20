
from datetime import datetime
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import MappedColumn, mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text, event

from src.shared.utils.xid import generate_xid

class SlotCalculationOrderConfiguration(BaseModel):
    __tablename__ = "va_slot_calculation_order_configurations"
    
    slot_calculation_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_slot_calculations.id"), primary_key=True,nullable=False
    )
    category_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_categories.id"), primary_key=True,nullable=False
    )
    forecast_percentage: MappedColumn[int] = mapped_column(Integer, nullable=False)
    urgent_percentage: MappedColumn[int] = mapped_column(Integer, nullable=False)
    
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
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))
    
    slot_calculation: Mapped["SlotCalculation"] = relationship("SlotCalculation")
    category: Mapped["Category"] = relationship("Category")
    
@event.listens_for(SlotCalculationOrderConfiguration, "before_insert")
def before_insert(mapper, connection, target: SlotCalculationOrderConfiguration):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(SlotCalculationOrderConfiguration, "before_update")
def before_update(mapper, connection, target: SlotCalculationOrderConfiguration):
    target.updated_at = datetime.now()
