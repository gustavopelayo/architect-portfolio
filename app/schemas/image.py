from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImageBase(BaseModel):
    id: int
    image_url: str
    caption: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImageCreate(BaseModel):
    image_url: str
    caption: Optional[str] = None
    is_technical: bool = False