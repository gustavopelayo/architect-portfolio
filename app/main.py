from fastapi import FastAPI, Form, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uvicorn
import shutil
from pathlib import Path
from datetime import datetime
from app.api.v1.endpoints import portfolio, auth
from app.db.session import get_db
from app.core.security import authenticate_user, create_access_token
from app.crud import portfolio as crud_portfolio

app = FastAPI(title="Architect Portfolio")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    from app.crud import portfolio as crud_portfolio
    featured = crud_portfolio.get_featured_portfolios(db)
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "featured_portfolios": featured})

@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request, db: Session = Depends(get_db)):
    from app.crud import portfolio as crud_portfolio
    portfolios = crud_portfolio.get_portfolios(db, skip=0, limit=100)
    return templates.TemplateResponse(request=request, name="portfolio.html", context={"request": request, "portfolios": portfolios})

@app.get("/portfolio/{portfolio_id}", response_class=HTMLResponse)
async def portfolio_detail(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    from app.crud import portfolio as crud_portfolio
    portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if not portfolio:
        return RedirectResponse(url="/portfolio", status_code=302)
    return templates.TemplateResponse(request=request, name="portfolio_detail.html", context={"request": request, "portfolio": portfolio})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, db: Session = Depends(get_db)):
    featured = crud_portfolio.get_featured_portfolios(db)
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={"request": request, "featured_portfolios": featured},
    )

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html", context={"request": request})

@app.post("/contact", response_class=HTMLResponse)
async def contact_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    # Log the form data (in a real application, you would send an email here)
    print(f"Contact form submission from {name} ({email}): {message}")
    # Redirect to the contact page with a success message
    return RedirectResponse(url="/contact?success=1", status_code=302)

# Admin routes
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request, error: str = None):
    return templates.TemplateResponse(request=request, name="admin/login.html", context={"request": request, "error": error})

@app.post("/admin/login")
async def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            request=request, 
            name="admin/login.html", 
            context={"request": request, "error": "Invalid credentials"}
        )
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=access_token)
    return response

@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    portfolios = crud_portfolio.get_portfolios(db, skip=0, limit=100)
    return templates.TemplateResponse(
        request=request, 
        name="admin/dashboard.html", 
        context={"request": request, "projects": portfolios}
    )

@app.get("/admin/projects/create", response_class=HTMLResponse)
async def create_project_form(request: Request):
    return templates.TemplateResponse(request=request, name="admin/project_form.html", context={"request": request})

@app.post("/admin/projects/create")
async def create_project(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    year: int = Form(None),
    location: str = Form(None),
    db: Session = Depends(get_db)
):
    from app.schemas.portfolio import PortfolioCreate
    portfolio_data = PortfolioCreate(
        name=name,
        description=description,
        year=year,
        location=location,
    )
    crud_portfolio.create_portfolio(db=db, portfolio=portfolio_data)
    return RedirectResponse(url="/admin/dashboard", status_code=302)

@app.get("/admin/projects/{portfolio_id}/edit", response_class=HTMLResponse)
async def edit_project_form(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if not portfolio:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse(
        request=request, 
        name="admin/project_form.html", 
        context={"request": request, "project": portfolio}
    )

@app.post("/admin/projects/{portfolio_id}/edit")
async def edit_project(
    request: Request,
    portfolio_id: int,
    name: str = Form(...),
    description: str = Form(None),
    year: int = Form(None),
    location: str = Form(None),
    db: Session = Depends(get_db)
):
    from app.schemas.portfolio import PortfolioUpdate
    portfolio_data = PortfolioUpdate(
        name=name,
        description=description,
        year=year,
        location=location,
    )
    crud_portfolio.update_portfolio(db=db, portfolio_id=portfolio_id, portfolio=portfolio_data)
    return RedirectResponse(url="/admin/dashboard", status_code=302)

@app.get("/admin/projects/{portfolio_id}/delete")
async def delete_project(portfolio_id: int, db: Session = Depends(get_db)):
    crud_portfolio.delete_portfolio(db=db, portfolio_id=portfolio_id)
    return RedirectResponse(url="/admin/dashboard", status_code=302)

@app.post("/admin/projects/{portfolio_id}/toggle-featured")
async def toggle_featured(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if portfolio:
        from app.schemas.portfolio import PortfolioUpdate
        crud_portfolio.update_portfolio(db, portfolio_id, PortfolioUpdate(is_featured=not portfolio.is_featured))
    return RedirectResponse(url="/admin/dashboard", status_code=302)

@app.post("/admin/projects/{portfolio_id}/upload-image")
async def upload_portfolio_image(
    portfolio_id: int,
    file: UploadFile = File(...),
    caption: str = Form(None),
    db: Session = Depends(get_db)
):
    portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if not portfolio:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    upload_dir = Path("app/static/uploads") / str(portfolio_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = Path(file.filename).suffix or ".jpg"
    filename = f"{portfolio_id}_{int(datetime.now().timestamp())}{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    from app.crud import image as crud_image
    from app.schemas.image import ImageCreate
    
    image_url = f"/static/uploads/{portfolio_id}/{filename}"
    image_data = ImageCreate(image_url=image_url, caption=caption)
    crud_image.create_portfolio_image(db=db, portfolio_id=portfolio_id, image=image_data)
    
    return RedirectResponse(url=f"/admin/projects/{portfolio_id}/edit", status_code=302)

@app.post("/admin/projects/{portfolio_id}/upload-technical")
async def upload_technical_drawing(
    portfolio_id: int,
    file: UploadFile = File(...),
    caption: str = Form(None),
    db: Session = Depends(get_db)
):
    portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if not portfolio:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    upload_dir = Path("app/static/uploads") / str(portfolio_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = Path(file.filename).suffix or ".jpg"
    filename = f"{portfolio_id}_tech_{int(datetime.now().timestamp())}{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    from app.crud import image as crud_image
    from app.schemas.image import ImageCreate
    
    image_url = f"/static/uploads/{portfolio_id}/{filename}"
    image_data = ImageCreate(image_url=image_url, caption=caption)
    crud_image.create_technical_image(db=db, portfolio_id=portfolio_id, image=image_data)
    
    return RedirectResponse(url=f"/admin/projects/{portfolio_id}/edit", status_code=302)

@app.get("/admin/images/{image_id}/delete")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    from app.models.image import PortfolioImage, TechnicalImage
    from pathlib import Path
    
    # Try to find image in both tables
    image = db.query(PortfolioImage).filter(PortfolioImage.id == image_id).first()
    if not image:
        image = db.query(TechnicalImage).filter(TechnicalImage.id == image_id).first()
    
    if not image:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    # Get portfolio_id before deleting
    portfolio_id = image.portfolio_id
    
    # Delete file from filesystem
    if image.image_url:
        file_path = Path("app") / image.image_url.lstrip("/")
        if file_path.exists():
            file_path.unlink()
    
    # Delete from database
    db.delete(image)
    db.commit()
    
    return RedirectResponse(url=f"/admin/projects/{portfolio_id}/edit", status_code=302)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
