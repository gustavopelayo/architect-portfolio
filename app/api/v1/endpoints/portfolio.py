from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.crud import portfolio as crud_portfolio
from app.crud import image as crud_image
from app.schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate
from app.schemas.image import ImageCreate
from app.api.deps import get_current_active_user
import os
import shutil
from pathlib import Path
from datetime import datetime

router = APIRouter()

# Portfolio endpoints
@router.get("/", response_model=List[Portfolio])
def read_portfolios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    portfolios = crud_portfolio.get_portfolios(db, skip=skip, limit=limit)
    return portfolios

@router.get("/featured", response_model=List[Portfolio])
def read_featured_portfolios(db: Session = Depends(get_db)):
    portfolios = crud_portfolio.get_featured_portfolios(db)
    return portfolios

@router.get("/{portfolio_id}", response_model=Portfolio)
def read_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    db_portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return db_portfolio

@router.post("/", response_model=Portfolio)
def create_portfolio_endpoint(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    return crud_portfolio.create_portfolio(db=db, portfolio=portfolio)

@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio_endpoint(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    db_portfolio = crud_portfolio.update_portfolio(db=db, portfolio_id=portfolio_id, portfolio=portfolio)
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return db_portfolio

@router.delete("/{portfolio_id}")
def delete_portfolio_endpoint(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    db_portfolio = crud_portfolio.delete_portfolio(db=db, portfolio_id=portfolio_id)
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"message": "Portfolio deleted successfully"}

# Image upload endpoint
@router.post("/{portfolio_id}/images")
async def upload_portfolio_image(
    portfolio_id: int,
    file: UploadFile = File(...),
    caption: str = None,
    is_technical: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    # Verify portfolio exists
    db_portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Create upload directory if it doesn't exist
    upload_dir = Path("app/static/uploads") / str(portfolio_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    filename = f"{portfolio_id}_{int(datetime.now().timestamp())}{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create image record
    image_data = ImageCreate(
        image_url=str(file_path),
        caption=caption,
        is_technical=is_technical
    )
    
    if is_technical:
        return crud_image.create_technical_image(db=db, portfolio_id=portfolio_id, image=image_data)
    else:
        return crud_image.create_portfolio_image(db=db, portfolio_id=portfolio_id, image=image_data)