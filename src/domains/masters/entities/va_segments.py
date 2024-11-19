
from src.shared.entities.basemodel import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, MappedColumn

class Segment(BaseModel):
    __tablename__ = "va_segments"
    id: MappedColumn[str] = mapped_column(String, primary_key=True, nullable=False)
    