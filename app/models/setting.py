from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False, default="")


class HeroImage(Base):
    __tablename__ = "hero_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(255), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    # Legacy single-language caption (keep for backward compatibility)
    caption = Column(String(255), nullable=True)
    # Bilingual captions
    caption_pt = Column(String(255), nullable=True)
    caption_en = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    
    portfolio = relationship("Portfolio", backref="hero_images")
