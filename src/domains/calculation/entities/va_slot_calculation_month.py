
from datetime import datetime
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text, event

from src.shared.utils.xid import generate_xid


class SlotCalculationMonth(BaseModel):
    __tablename__ = "va_slot_calculation_months"
    
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    slot_calculation_model_id: MappedColumn[str] = mapped_column(String (255), ForeignKey('va_slot_calculation_models.id'),nullable=False)
    forecast_month: MappedColumn[int] = mapped_column(Integer, nullable=False)
    take_off: MappedColumn[int] = mapped_column(Integer, nullable=False)
    bo: MappedColumn[int] = mapped_column(Integer, nullable=False)
    remaining: MappedColumn[int] = mapped_column(Integer, nullable=False)
    stock_pilot: MappedColumn[int] = mapped_column(Integer, nullable=False)
    soa: MappedColumn[int] = mapped_column(Integer, nullable=False)
    oc: MappedColumn[int] = mapped_column(Integer, nullable=False)
    booking: MappedColumn[int] = mapped_column(Integer, nullable=False)
    forecast_order: MappedColumn[int] = mapped_column(Integer, nullable=False)
    urgent_order: MappedColumn[int] = mapped_column(Integer, nullable=False)
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
    
    slot_calculation_model: MappedColumn["SlotCalculationModel"] = relationship("SlotCalculationModel")
    
@event.listens_for(SlotCalculationMonth, "before_insert")
def before_insert(mapper, connection, target: SlotCalculationMonth):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(SlotCalculationMonth, "before_update")
def before_update(mapper, connection, target: SlotCalculationMonth):
    target.updated_at = datetime.now()