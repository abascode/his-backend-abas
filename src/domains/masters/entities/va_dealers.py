
from src.shared.entities.basemodel import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, MappedColumn

class Dealer(BaseModel):
    __tablename__ = "va_dealers"
    id: MappedColumn[str] = mapped_column(String, primary_key=True, nullable=False)
    name: MappedColumn[str] = mapped_column(String, nullable=False)