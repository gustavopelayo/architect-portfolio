from sqlalchemy import Column, Integer, String, Text
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
    caption = Column(String(255))
    sort_order = Column(Integer, default=0)
