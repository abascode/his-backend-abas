
from datetime import datetime
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import MappedColumn, mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text, event

from src.shared.utils.xid import generate_xid

class SlotCalculationStockPilot(BaseModel):
    __tablename__ = "va_slot_calculation_stock_pilots"
    
    slot_calculation_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_slot_calculations.id", onupdate="CASCADE"), primary_key=True,nullable=False
    )
    segment_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_segments.id", onupdate="CASCADE"), primary_key=True,nullable=False
    )
    percentage: MappedColumn[int] = mapped_column(Integer, nullable=False)
    
    
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
    segment: Mapped["Segment"] = relationship("Segment")
    
@event.listens_for(SlotCalculationStockPilot, "before_insert")
def before_insert(mapper, connection, target: SlotCalculationStockPilot):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(SlotCalculationStockPilot, "before_update")
def before_update(mapper, connection, target: SlotCalculationStockPilot):
    target.updated_at = datetime.now()
