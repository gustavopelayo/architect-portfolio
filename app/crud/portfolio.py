from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.models.image import PortfolioImage, TechnicalImage
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate

def get_portfolio(db: Session, portfolio_id: int):
    return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

def get_portfolios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Portfolio).offset(skip).limit(limit).all()

def get_featured_portfolios(db: Session, limit: int = 10):
    return db.query(Portfolio).filter(Portfolio.is_featured == True).limit(limit).all()

def create_portfolio(db: Session, portfolio: PortfolioCreate):
    db_portfolio = Portfolio(
        name=portfolio.name,
        description=portfolio.description,
        year=portfolio.year,
        location=portfolio.location,
        is_featured=portfolio.is_featured
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def update_portfolio(db: Session, portfolio_id: int, portfolio: PortfolioUpdate):
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if db_portfolio:
        portfolio_data = portfolio.dict(exclude_unset=True)
        for key, value in portfolio_data.items():
            setattr(db_portfolio, key, value)
        db.commit()
        db.refresh(db_portfolio)
    return db_portfolio

def delete_portfolio(db: Session, portfolio_id: int):
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if db_portfolio:
        db.delete(db_portfolio)
        db.commit()
    return db_portfolio