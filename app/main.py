from fastapi import FastAPI, Form, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uvicorn
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from app.api.v1.endpoints import portfolio, auth
from app.db.session import get_db
from app.core.security import authenticate_user, create_access_token
from app.crud import portfolio as crud_portfolio
from app.core.settings_helper import get_site_settings
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="Architect Portfolio")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

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
    from app.models.image import PortfolioImage
    site_settings = get_site_settings()
    featured = crud_portfolio.get_featured_portfolios(db)
    project_images_map = {}
    for p in featured:
        urls = [img.image_url for img in db.query(PortfolioImage).filter(PortfolioImage.portfolio_id == p.id).order_by(PortfolioImage.id).all()]
        if urls:
            project_images_map[str(p.id)] = urls
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request,
        "featured_portfolios": featured,
        "settings": site_settings,
        "project_images_map": project_images_map,
    })

@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request, db: Session = Depends(get_db)):
    from app.crud import portfolio as crud_portfolio
    site_settings = get_site_settings()
    portfolios = crud_portfolio.get_portfolios(db, skip=0, limit=100)
    return templates.TemplateResponse(request=request, name="portfolio.html", context={"request": request, "portfolios": portfolios, "settings": site_settings})

@app.get("/portfolio/{portfolio_id}", response_class=HTMLResponse)
async def portfolio_detail(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    from app.crud import portfolio as crud_portfolio
    site_settings = get_site_settings()
    portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if not portfolio:
        return RedirectResponse(url="/portfolio", status_code=302)
    return templates.TemplateResponse(request=request, name="portfolio_detail.html", context={"request": request, "portfolio": portfolio, "settings": site_settings})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, db: Session = Depends(get_db)):
    site_settings = get_site_settings()
    featured = crud_portfolio.get_featured_portfolios(db)
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={"request": request, "featured_portfolios": featured, "settings": site_settings},
    )

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    site_settings = get_site_settings()
    return templates.TemplateResponse(request=request, name="contact.html", context={"request": request, "settings": site_settings})

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
    site_settings = get_site_settings()
    return templates.TemplateResponse(request=request, name="admin/login.html", context={"request": request, "error": error, "settings": site_settings})

@app.post("/admin/login")
async def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        site_settings = get_site_settings()
        return templates.TemplateResponse(
            request=request, 
            name="admin/login.html", 
            context={"request": request, "error": "Invalid credentials", "settings": site_settings}
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
    site_settings = get_site_settings()
    portfolios = crud_portfolio.get_portfolios(db, skip=0, limit=100)
    return templates.TemplateResponse(
        request=request, 
        name="admin/dashboard.html", 
        context={"request": request, "projects": portfolios, "settings": site_settings}
    )

@app.get("/admin/projects/create", response_class=HTMLResponse)
async def create_project_form(request: Request):
    site_settings = get_site_settings()
    return templates.TemplateResponse(request=request, name="admin/project_form.html", context={"request": request, "settings": site_settings})

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
    site_settings = get_site_settings()
    portfolio = crud_portfolio.get_portfolio(db, portfolio_id=portfolio_id)
    if not portfolio:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse(
        request=request, 
        name="admin/project_form.html", 
        context={"request": request, "project": portfolio, "settings": site_settings}
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

@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, db: Session = Depends(get_db)):
    from app.models.setting import SiteSetting, HeroImage
    from app.models.image import PortfolioImage, TechnicalImage
    settings_list = {r.key: r.value for r in db.query(SiteSetting).all()}
    hero_images = db.query(HeroImage).order_by(HeroImage.sort_order).all()
    site_settings = get_site_settings()
    project_images = db.query(PortfolioImage).all() + db.query(TechnicalImage).all()
    existing_hero_urls = {h.image_url for h in hero_images}
    return templates.TemplateResponse(
        request=request,
        name="admin/settings.html",
        context={
            "request": request,
            "settings_list": settings_list,
            "hero_images": hero_images,
            "settings": site_settings,
            "project_images": project_images,
            "existing_hero_urls": existing_hero_urls,
        }
    )

@app.post("/admin/settings/site-name")
async def update_site_name(
    site_name: str = Form(...),
    copyright: str = Form(None),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    for key, value in {"site_name": site_name, "copyright": copyright}.items():
        if value is not None:
            row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
            if row:
                row.value = value
            else:
                db.add(SiteSetting(key=key, value=value))
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

@app.post("/admin/settings/taglines")
async def update_taglines(
    request: Request,
    taglines: str = Form(...),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    row = db.query(SiteSetting).filter(SiteSetting.key == "tagline").first()
    if row:
        row.value = taglines
    else:
        db.add(SiteSetting(key="tagline", value=taglines))
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

@app.post("/admin/settings/logo")
async def upload_logo(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    import time
    upload_dir = Path("app/static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix or ".png"
    filename = f"logo{ext}"
    filepath = upload_dir / filename
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Add timestamp for cache-busting
    timestamp = int(time.time())
    logo_url = f"/static/uploads/{filename}?v={timestamp}"
    
    row = db.query(SiteSetting).filter(SiteSetting.key == "logo_path").first()
    if row:
        row.value = logo_url
    else:
        db.add(SiteSetting(key="logo_path", value=logo_url))
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

@app.post("/admin/settings/hero")
async def upload_hero_image(
    request: Request,
    file: UploadFile = File(...),
    caption: str = Form(None),
    db: Session = Depends(get_db)
):
    from app.models.setting import HeroImage
    from sqlalchemy import func as sa_func
    upload_dir = Path("app/static/uploads/hero")
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"hero_{uuid.uuid4().hex[:12]}{ext}"
    filepath = upload_dir / filename
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    max_order = db.query(sa_func.max(HeroImage.sort_order)).scalar() or 0
    db.add(HeroImage(
        image_url=f"/static/uploads/hero/{filename}",
        caption=caption,
        sort_order=max_order + 1
    ))
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

@app.get("/admin/settings/hero/{hero_id}/delete")
async def delete_hero_image(hero_id: int, db: Session = Depends(get_db)):
    from app.models.setting import HeroImage
    img = db.query(HeroImage).filter(HeroImage.id == hero_id).first()
    if img:
        filepath = Path("app") / img.image_url.lstrip("/")
        if filepath.exists():
            filepath.unlink()
        db.delete(img)
        db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

@app.get("/admin/settings/hero/add-from-project")
async def add_hero_from_project(image_url: str, db: Session = Depends(get_db)):
    from app.models.setting import HeroImage
    from sqlalchemy import func as sa_func
    existing = db.query(HeroImage).filter(HeroImage.image_url == image_url).first()
    if not existing:
        max_order = db.query(sa_func.max(HeroImage.sort_order)).scalar() or 0
        db.add(HeroImage(image_url=image_url, sort_order=max_order + 1))
        db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

@app.post("/admin/settings/contact")
async def update_contact(
    request: Request,
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    blurb: str = Form(None),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    updates = {
        "contact_email": email,
        "contact_phone": phone,
        "contact_address": address,
        "contact_blurb": blurb,
    }
    for key, value in updates.items():
        if value is not None:
            row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
            if row:
                row.value = value
            else:
                db.add(SiteSetting(key=key, value=value))
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

@app.post("/admin/settings/about")
async def update_about(
    request: Request,
    title: str = Form(None),
    body: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    if title is not None:
        row = db.query(SiteSetting).filter(SiteSetting.key == "about_title").first()
        if row:
            row.value = title
        else:
            db.add(SiteSetting(key="about_title", value=title))
    if body is not None:
        row = db.query(SiteSetting).filter(SiteSetting.key == "about_body").first()
        if row:
            row.value = body
        else:
            db.add(SiteSetting(key="about_body", value=body))
    if file and file.filename:
        upload_dir = Path("app/static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename).suffix or ".jpg"
        filename = f"about_image{ext}"
        filepath = upload_dir / filename
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)
        img_url = f"/static/uploads/{filename}"
        row = db.query(SiteSetting).filter(SiteSetting.key == "about_image").first()
        if row:
            row.value = img_url
        else:
            db.add(SiteSetting(key="about_image", value=img_url))
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)

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
    
    suffix = Path(file.filename).suffix.lower()
    uid = uuid.uuid4().hex[:12]
    
    if suffix == ".pdf":
        import fitz
        temp = upload_dir / f"temp_{uid}.pdf"
        with open(temp, "wb") as f:
            shutil.copyfileobj(file.file, f)
        doc = fitz.open(temp)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        filename = f"{portfolio_id}_{uid}.png"
        pix.save(str(upload_dir / filename))
        doc.close()
        temp.unlink()
    elif suffix in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        filename = f"{portfolio_id}_{uid}{suffix}"
        file_path = upload_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        return RedirectResponse(url=f"/admin/projects/{portfolio_id}/edit", status_code=302)
    
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
    
    upload_dir = Path("app/static/uploads") / str(portfolio_id) / "technical"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    suffix = Path(file.filename).suffix.lower()
    uid = uuid.uuid4().hex[:12]
    
    if suffix == ".pdf":
        import fitz
        temp = upload_dir / f"temp_{uid}.pdf"
        with open(temp, "wb") as f:
            shutil.copyfileobj(file.file, f)
        doc = fitz.open(temp)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        filename = f"{portfolio_id}_tech_{uid}.png"
        pix.save(str(upload_dir / filename))
        doc.close()
        temp.unlink()
    else:
        filename = f"{portfolio_id}_tech_{uid}{suffix}"
        file_path = upload_dir / filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    
    from app.crud import image as crud_image
    from app.schemas.image import ImageCreate
    
    image_url = f"/static/uploads/{portfolio_id}/technical/{filename}"
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

@app.get("/admin/projects/{portfolio_id}/images/{image_id}/set-cover")
async def set_cover_image(portfolio_id: int, image_id: int, db: Session = Depends(get_db)):
    from app.models.image import PortfolioImage, TechnicalImage
    db.query(PortfolioImage).filter(PortfolioImage.portfolio_id == portfolio_id).update({"is_cover": False})
    db.query(TechnicalImage).filter(TechnicalImage.portfolio_id == portfolio_id).update({"is_cover": False})
    for model in (PortfolioImage, TechnicalImage):
        img = db.query(model).filter(model.id == image_id, model.portfolio_id == portfolio_id).first()
        if img:
            img.is_cover = True
            break
    db.commit()
    return RedirectResponse(url=f"/admin/projects/{portfolio_id}/edit", status_code=302)

@app.post("/admin/images/{image_id}/caption")
async def update_caption(image_id: int, caption: str = Form(""), db: Session = Depends(get_db)):
    from app.models.image import PortfolioImage, TechnicalImage
    for model in (PortfolioImage, TechnicalImage):
        img = db.query(model).filter(model.id == image_id).first()
        if img:
            img.caption = caption
            db.commit()
            return RedirectResponse(url=f"/admin/projects/{img.portfolio_id}/edit", status_code=302)
    return RedirectResponse(url="/admin/dashboard", status_code=302)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
