from sqlalchemy.orm import Session
from app.models.image import PortfolioImage, TechnicalImage
from app.schemas.image import ImageCreate

def create_portfolio_image(db: Session, portfolio_id: int, image: ImageCreate):
    db_image = PortfolioImage(
        portfolio_id=portfolio_id,
        image_url=image.image_url,
        caption=image.caption,
        is_technical=image.is_technical
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def create_technical_image(db: Session, portfolio_id: int, image: ImageCreate):
    db_image = TechnicalImage(
        portfolio_id=portfolio_id,
        image_url=image.image_url,
        caption=image.caption
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_portfolio_images(db: Session, portfolio_id: int):
    return db.query(PortfolioImage).filter(PortfolioImage.portfolio_id == portfolio_id).all()

def get_technical_images(db: Session, portfolio_id: int):
    return db.query(TechnicalImage).filter(TechnicalImage.portfolio_id == portfolio_id).all()

def delete_image(db: Session, image_id: int, image_type: str = "portfolio"):
    if image_type == "technical":
        db_image = db.query(TechnicalImage).filter(TechnicalImage.id == image_id).first()
    else:
        db_image = db.query(PortfolioImage).filter(PortfolioImage.id == image_id).first()
    
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image