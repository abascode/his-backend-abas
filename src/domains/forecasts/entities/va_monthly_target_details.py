from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text, event
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship, Mapped
from datetime import datetime


class MonthlyTargetDetail(BaseModel):
    __tablename__ = "va_monthly_target_details"
    month_target_id: MappedColumn[str] = mapped_column(
        String,
        ForeignKey("va_monthly_targets.id", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    forecast_month: MappedColumn[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    dealer_id: MappedColumn[str] = mapped_column(
        String,
        ForeignKey("va_dealers.id", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    target: MappedColumn[int] = mapped_column(Integer, nullable=False)
    category_id: MappedColumn[str] = mapped_column(
        String,
        ForeignKey("va_categories.id", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
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

    monthly_target: Mapped["MonthlyTarget"] = relationship(
        "MonthlyTarget", back_populates="details"
    )
    dealer: Mapped["Dealer"] = relationship("Dealer")
    category: Mapped["Category"] = relationship("Category")


@event.listens_for(MonthlyTargetDetail, "before_insert")
def before_insert(mapper, connection, target: MonthlyTargetDetail):
    target.created_at = datetime.now()


@event.listens_for(MonthlyTargetDetail, "before_update")
def before_update(mapper, connection, target: MonthlyTargetDetail):
    target.updated_at = datetime.now()
