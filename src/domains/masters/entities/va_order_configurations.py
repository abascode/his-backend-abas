
from src.shared.entities.basemodel import BaseModel
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import MappedColumn, mapped_column, Mapped, relationship

from src.shared.entities.basemodel import BaseModel

class OrderConfiguration(BaseModel):
    __tablename__ = 'va_order_configurations'
    
    month: MappedColumn[int] = mapped_column(Integer, primary_key=True, nullable=False)
    year: MappedColumn[int] = mapped_column(Integer, primary_key=True, nullable=False)
    category_id: MappedColumn[str] = mapped_column(String(255), ForeignKey("va_categories.id"),primary_key=True, nullable=False)
    forecast_percentage: MappedColumn[int] = mapped_column(Integer, nullable=False)
    urgent_percentage: MappedColumn[int] = mapped_column(Integer, nullable=False)
    
    category: Mapped['Category'] = relationship("Category")