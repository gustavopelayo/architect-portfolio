from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PortfolioImage(Base):
    __tablename__ = "portfolio_images"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    image_url = Column(String(255), nullable=False)
    is_technical = Column(Boolean, default=False)  # False = regular photo, True = technical drawing
    is_cover = Column(Boolean, default=False)
    # Legacy single-language caption (keep for backward compatibility)
    caption = Column(String(255), nullable=True)
    # Bilingual captions
    caption_pt = Column(String(255), nullable=True)
    caption_en = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    portfolio = relationship("Portfolio", backref="images")

class TechnicalImage(Base):
    __tablename__ = "technical_images"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    image_url = Column(String(255), nullable=False)
    is_cover = Column(Boolean, default=False)
    # Legacy single-language caption (keep for backward compatibility)
    caption = Column(String(255), nullable=True)
    # Bilingual captions
    caption_pt = Column(String(255), nullable=True)
    caption_en = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    portfolio = relationship("Portfolio", backref="technical_images")