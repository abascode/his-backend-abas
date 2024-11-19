from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import MappedColumn, mapped_column, Mapped, relationship
from src.shared.entities.basemodel import BaseModel

class StockPilot(BaseModel):
    __tablename__ = "va_stock_pilots"
    
    month: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    segment_id: MappedColumn[str] = mapped_column(String(255), ForeignKey("va_segments.id"), primary_key=True,nullable=False)
    percentage: MappedColumn[int] = mapped_column(Integer, nullable=False)
    
    segment: Mapped['Segment'] = relationship("Segment")