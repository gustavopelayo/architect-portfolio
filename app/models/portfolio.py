from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    # Legacy single-language fields (keep for backward compatibility)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    # Bilingual fields
    name_pt = Column(String(255), nullable=True)
    name_en = Column(String(255), nullable=True)
    description_pt = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    location_pt = Column(String(255), nullable=True)
    location_en = Column(String(255), nullable=True)
    # Other fields
    year = Column(Integer)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())