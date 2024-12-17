from datetime import datetime
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import MappedColumn, mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text, event

from src.shared.utils.xid import generate_xid


class SlotCalculationDetail(BaseModel):
    __tablename__ = "va_slot_calculation_details"

    slot_calculation_id: MappedColumn[str] = mapped_column(
        String(255),
        ForeignKey("va_slot_calculations.id", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    model_id: MappedColumn[str] = mapped_column(
        String(255),
        ForeignKey("va_models.id", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    forecast_month: MappedColumn[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    take_off: MappedColumn[int] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    bo: MappedColumn[int] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    soa: MappedColumn[int] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    so: MappedColumn[int] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    oc: MappedColumn[int] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    booking_prospect: MappedColumn[int] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )

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
    model: Mapped["Model"] = relationship("Model")


@event.listens_for(SlotCalculationDetail, "before_insert")
def before_insert(mapper, connection, target: SlotCalculationDetail):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(SlotCalculationDetail, "before_update")
def before_update(mapper, connection, target: SlotCalculationDetail):
    target.updated_at = datetime.now()
