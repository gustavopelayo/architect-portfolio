from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.image import ImageBase

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None
    year: Optional[int] = None
    location: Optional[str] = None
    is_featured: Optional[bool] = False

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    location: Optional[str] = None
    is_featured: Optional[bool] = None

class PortfolioInDBBase(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PortfolioInDB(PortfolioInDBBase):
    pass

class Portfolio(PortfolioInDBBase):
    images: List[ImageBase] = []
    technical_images: List[ImageBase] = []