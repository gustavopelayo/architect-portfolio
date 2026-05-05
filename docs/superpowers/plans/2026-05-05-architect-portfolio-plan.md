# Architect Portfolio Website Implementation Plan

Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a monolithic FastAPI + Jinja2 Templates portfolio website for architects with backoffice CMS, inspired by the clean aesthetic of andre tavares.net

**Architecture:** Single codebase with FastAPI backend serving both API endpoints and server-rendered HTML templates. MySQL database for data persistence with SQLAlchemy ORM. The backend handles authentication, CRUD operations for portfolio items, and template rendering.

**Tech Stack:** FastAPI (Python), Jinja2 Templates, MySQL, SQLAlchemy, Pydantic, Passlib (for password hashing), Python-multipart (for file uploads)

---

### Task 1: Initialize Python project and install dependencies

**Files:**
- Create: `requirements.txt`
- Create: `app/main.py`

- [ ] **Step 1: Create requirements.txt with core dependencies**

```txt
fastapi>=0.68.0
uvicorn>=0.15.0
sqlalchemy>=1.4.0
mysql-connector-python>=8.0.0
alembic>=1.7.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.0
python-multipart>=0.0.5
pydantic>=1.8.0
jinja2>=3.0.0
aiofiles>=0.8.0
pillow>=8.0.0
```

- [ ] **Step 2: Create basic FastAPI main application**

```python
from fastapi import FastAPI

app = FastAPI(title="Architect Portfolio API")

@app.get("/")
async def root():
    return {"message": "Architect Portfolio API"}
```

- [ ] **Step 3: Verify setup works**

Run: `uvicorn app.main:app --reload`
Expected: Server starts on http://127.0.0.1:8000

- [ ] **Step 4: Commit initial setup**

```bash
git add requirements.txt app/main.py
git commit -m "feat: initialize project with FastAPI dependencies"
```

### Task 2: Set up database configuration and models

**Files:**
- Create: `app/db/base.py`
- Create: `app/db/session.py`
- Create: `app/models/portfolio.py`
- Create: `app/models/image.py`
- Create: `app/models/user.py`

- [ ] **Step 1: Create database base class**

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

- [ ] **Step 2: Create database session manager**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/architect_portfolio")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 3: Create Portfolio model**

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    year = Column(Integer)
    location = Column(String(255))
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

- [ ] **Step 4: Create Image models**

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PortfolioImage(Base):
    __tablename__ = "portfolio_images"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    image_url = Column(String(255), nullable=False)
    is_technical = Column(Boolean, default=False)  # False = regular photo, True = technical drawing
    caption = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    portfolio = relationship("Portfolio", backref="images")

class TechnicalImage(Base):
    __tablename__ = "technical_images"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    image_url = Column(String(255), nullable=False)
    caption = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    portfolio = relationship("Portfolio", backref="technical_images")
```

- [ ] **Step 5: Create User model for authentication**

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

- [ ] **Step 6: Commit database setup**

```bash
git add app/db/base.py app/db/session.py app/models/portfolio.py app/models/image.py app/models/user.py
git commit -m "feat: set up database configuration and models"
```

## Chunk 2: Authentication and Security

### Task 7: Set up authentication utilities

**Files:**
- Create: `app/core/security.py`
- Create: `app/core/config.py`
- Create: `app/api/v1/endpoints/auth.py`

- [ ] **Step 1: Create security utilities for password hashing and token generation**

```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

- [ ] **Step 2: Create configuration settings**

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Architect Portfolio"
    SECRET_KEY: str = "your-secret-key-here"  # Should be loaded from env in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost/architect_portfolio"
    
    class Config:
        case_sensitive = True

settings = Settings()
```

- [ ] **Step 3: Create authentication endpoints**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.core.security import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.schemas.user import Token

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
```

- [ ] **Step 4: Commit authentication setup**

```bash
git add app/core/security.py app/core/config.py app/api/v1/endpoints/auth.py
git commit -m "feat: set up authentication utilities and endpoints"
```

### Task 8: Create user schemas and dependencies

**Files:**
- Create: `app/schemas/user.py`
- Create: `app/api/deps.py`

- [ ] **Step 1: Create user schemas**

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserInDB(UserInDBBase):
    hashed_password: str

class User(UserInDBBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
```

- [ ] **Step 2: Create authentication dependencies**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User
from app.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

- [ ] **Step 3: Commit authentication schemas and dependencies**

```bash
git add app/schemas/user.py app/api/deps.py
git commit -m "feat: create user schemas and authentication dependencies"
```

## Chunk 3: Portfolio API Endpoints

### Task 9: Set up portfolio schemas

**Files:**
- Create: `app/schemas/portfolio.py`
- Create: `app/schemas/image.py`

- [ ] **Step 1: Create portfolio schemas**

```python
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
        orm_mode = True

class PortfolioInDB(PortfolioInDBBase):
    pass

class Portfolio(PortfolioInDBBase):
    images: List[ImageBase] = []
    technical_images: List[ImageBase] = []
```

- [ ] **Step 2: Create image schemas**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImageBase(BaseModel):
    id: int
    image_url: str
    caption: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class ImageCreate(BaseModel):
    image_url: str
    caption: Optional[str] = None
    is_technical: bool = False
```

- [ ] **Step 3: Commit portfolio schemas**

```bash
git add app/schemas/portfolio.py app/schemas/image.py
git commit -m "feat: create portfolio and image schemas"
```

### Task 10: Set up portfolio CRUD operations

**Files:**
- Create: `app/crud/portfolio.py`
- Create: `app/crud/image.py`
- Create: `app/api/v1/endpoints/portfolio.py`

- [ ] **Step 1: Create portfolio CRUD operations**

```python
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
```

- [ ] **Step 2: Create image CRUD operations**

```python
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
```

- [ ] **Step 3: Create portfolio API endpoints**

```python
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

# Include authentication router
from app.api.v1.endpoints import auth
router.include_router(auth.router, prefix="/auth", tags=["auth"])
```

- [ ] **Step 4: Commit portfolio CRUD and API endpoints**

```bash
git add app/crud/portfolio.py app/crud/image.py app/api/v1/endpoints/portfolio.py
git commit -m "feat: set up portfolio CRUD operations and API endpoints"
```

## Chunk 4: Frontend Templates and Static Files

### Task 11: Set up template configuration and base templates

**Files:**
- Create: `app/templates/base.html`
- Create: `app/templates/index.html`
- Create: `app/templates/portfolio.html`
- Create: `app/templates/portfolio_detail.html`
- Create: `app/templates/about.html`
- Create: `app/templates/contact.html`

- [ ] **Step 1: Create base template with andre tavares.net inspired styling**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Architect Portfolio{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', path='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@300;400;600&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <nav class="navbar">
            <div class="container">
                <a href="/" class="logo">Architect Portfolio</a>
                <ul class="nav-links">
                    <li><a href="/">Home</a></li>
                    <li><a href="/portfolio">Projects</a></li>
                    <li><a href="/about">About</a></li>
                    <li><a href="/contact">Contact</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <main>
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; {{ year }} Architect Portfolio. All rights reserved.</p>
        </div>
    </footer>

    <script src="{{ url_for('static', path='js/main.js') }}"></script>
</body>
</html>
```

- [ ] **Step 2: Create homepage template**

```html
{% extends "base.html" %}

{% block title %}Home - Architect Portfolio{% endblock %}

{% block content %}
<section class="hero">
    <div class="hero-content">
        <h1>Architectural Design Portfolio</h1>
        <p>Innovative and sustainable architectural solutions</p>
        <a href="/portfolio" class="btn-primary">View Projects</a>
    </div>
</section>

<section class="featured-projects">
    <h2>Featured Projects</h2>
    <div class="projects-grid">
        {% for portfolio in featured_portfolios %}
        <article class="project-card">
            <a href="/portfolio/{{ portfolio.id }}">
                {% if portfolio.images %}
                <img src="{{ portfolio.images[0].image_url }}" alt="{{ portfolio.name }}">
                {% else %}
                <img src="/static/images/placeholder.jpg" alt="Project Image">
                {% endif %}
                <h3>{{ portfolio.name }}</h3>
                <p class="project-year">{{ portfolio.year }}</p>
            </a>
        </article>
        {% endfor %}
    </div>
</section>

<section class="about-preview">
    <h2>About the Studio</h2>
    <p>We specialize in creating timeless architectural designs that blend functionality with aesthetic excellence.</p>
    <a href="/about" class="btn-secondary">Learn More</a>
</section>
{% endblock %}
```

- [ ] **Step 3: Create portfolio listing template**

```html
{% extends "base.html" %}

{% block title %}Projects - Architect Portfolio{% endblock %}

{% block content %}
<section class="page-header">
    <h1>Our Projects</h1>
    <p>Explore our architectural portfolio</p>
</section>

{% if portfolios %}
<div class="projects-grid">
    {% for portfolio in portfolios %}
    <article class="project-card">
        <a href="/portfolio/{{ portfolio.id }}">
            {% if portfolio.images %}
            <img src="{{ portfolio.images[0].image_url }}" alt="{{ portfolio.name }}">
            {% else %}
            <img src="/static/images/placeholder.jpg" alt="Project Image">
            {% endif %}
            <div class="project-info">
                <h3>{{ portfolio.name }}</h3>
                <p class="project-location">{{ portfolio.location }}</p>
                <p class="project-year">{{ portfolio.year }}</p>
            </div>
        </a>
    </article>
    {% endfor %}
</div>
{% else %}
<p>No projects found.</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 4: Create portfolio detail template**

```html
{% extends "base.html" %}

{% block title %}{{ portfolio.name }} - Architect Portfolio{% endblock %}

{% block content %}
<section class="project-header">
    <div class="container">
        <h1>{{ portfolio.name }}</h1>
        <div class="project-meta">
            <span class="project-year">{{ portfolio.year }}</span>
            <span class="project-location">{{ portfolio.location }}</span>
        </div>
    </div>
</section>

<section class="project-gallery">
    <div class="container">
        {% if portfolio.images %}
        <div class="image-grid-main">
            {% for image in portfolio.images %}
            <div class="image-item">
                <img src="{{ image.image_url }}" alt="{{ portfolio.name }} - {{ image.caption or 'Image' }}">
                {% if image.caption %}
                <div class="image-caption">{{ image.caption }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if portfolio.technical_images %}
        <div class="technical-section">
            <h2>Technical Drawings</h2>
            <div class="image-grid-technical">
                {% for image in portfolio.technical_images %}
                <div class="image-item">
                    <img src="{{ image.image_url }}" alt="{{ portfolio.name }} - Technical {{ image.caption or 'Drawing' }}">
                    {% if image.caption %}
                    <div class="image-caption">{{ image.caption }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</section>

<section class="project-description">
    <div class="container">
        <h2>Project Description</h2>
        <div class="description-content">
            {{ portfolio.description | safe }}
        </div>
    </div>
</section>
{% endblock %}
```

- [ ] **Step 5: Create about and contact templates**

```html
<!-- about.html -->
{% extends "base.html" %}

{% block title %}About - Architect Portfolio{% endblock %}

{% block content %}
<section class="about-header">
    <div class="container">
        <h1>About the Studio</h1>
    </div>
</section>

<section class="about-content">
    <div class="container">
        <div class="about-text">
            <h2>Our Philosophy</h2>
            <p>We believe that architecture should enhance the human experience while respecting the environment. Our approach combines innovative design with sustainable practices to create spaces that are both beautiful and responsible.</p>
            <h2>Our Approach</h2>
            <p>Each project begins with a deep understanding of the site, the client's needs, and the cultural context. We strive to create designs that are timeless, functional, and inspiring.</p>
        </div>
        <div class="about-image">
            <img src="/static/images/about.jpg" alt="Architect at work">
        </div>
    </div>
</section>
{% endblock %}
```

```html
<!-- contact.html -->
{% extends "base.html" %}

{% block title %}Contact - Architect Portfolio{% endblock %}

{% block content %}
<section class="contact-header">
    <div class="container">
        <h1>Get in Touch</h1>
    </div>
</section>

<section class="contact-content">
    <div class="container">
        <form action="/contact" method="POST" class="contact-form">
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="subject">Subject</label>
                <input type="text" id="subject" name="subject" required>
            </div>
            <div class="form-group">
                <label for="message">Message</label>
                <textarea id="message" name="message" rows="5" required></textarea>
            </div>
            <button type="submit" class="btn-primary">Send Message</button>
        </form>
        
        <div class="contact-info">
            <h2>Studio Information</h2>
            <p>123 Architecture Street<br>City, State 12345<br>Phone: (123) 456-7890<br>Email: info@architectportfolio.com</p>
        </div>
    </div>
</section>
{% endblock %}
```

- [ ] **Step 6: Commit frontend templates**

```bash
git add app/templates/base.html app/templates/index.html app/templates/portfolio.html app/templates/portfolio_detail.html app/templates/about.html app/templates/contact.html
git commit -m "feat: create frontend templates with andre tavares.net inspired design"
```

### Task 12: Set up static files and CSS styling

**Files:**
- Create: `app/static/css/style.css`
- Create: `app/static/js/main.js`
- Create: `app/static/images/placeholder.jpg` (placeholder image)

- [ ] **Step 1: Create CSS styling inspired by andre tavares.net**

```css
/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Source Sans Pro', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif;
    margin-bottom: 1rem;
    color: #222;
}

p {
    margin-bottom: 1.5rem;
}

a {
    color: inherit;
    text-decoration: none;
    transition: color 0.3s ease;
}

a:hover {
    color: #0066cc;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Header and navigation */
header {
    background-color: #fff;
    border-bottom: 1px solid #eee;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 0;
}

.logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #222;
}

.nav-links {
    display: flex;
    list-style: none;
}

.nav-links li {
    margin-left: 2.5rem;
}

.nav-links a {
    font-weight: 400;
    font-size: 1rem;
    padding: 0.5rem 0;
    border-bottom: 2px solid transparent;
    transition: border-color 0.3s ease;
}

.nav-links a:hover {
    border-color: #0066cc;
}

/* Hero section */
.hero {
    background-color: #f8f9fa;
    padding: 8rem 0;
    text-align: center;
}

.hero-content h1 {
    font-size: 3.5rem;
    margin-bottom: 1.5rem;
    line-height: 1.2;
}

.hero-content p {
    font-size: 1.5rem;
    margin-bottom: 2.5rem;
    color: #666;
}

.btn-primary {
    display: inline-block;
    background-color: #222;
    color: #fff;
    padding: 1rem 2.5rem;
    border-radius: 0;
    font-weight: 600;
    transition: background-color 0.3s ease;
}

.btn-primary:hover {
    background-color: #000;
}

.btn-secondary {
    display: inline-block;
    background-color: transparent;
    color: #222;
    padding: 1rem 2.5rem;
    border: 2px solid #222;
    border-radius: 0;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background-color: #222;
    color: #fff;
}

/* Projects grid */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
    margin: 4rem 0;
}

.project-card {
    background-color: #fff;
    border: 1px solid #eee;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.project-card img {
    width: 100%;
    height: 250px;
    object-fit: cover;
    display: block;
}

.project-info {
    padding: 1.5rem;
}

.project-info h3 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.project-location {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 0.5rem;
}

.project-year {
    font-size: 0.9rem;
    font-weight: 600;
    color: #222;
}

/* Page header */
.page-header {
    text-align: center;
    padding: 4rem 0 2rem;
}

.page-header h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.page-header p {
    font-size: 1.2rem;
    color: #666;
    max-width: 600px;
    margin: 0 auto;
}

/* Project detail styles */
.project-header {
    background-color: #f8f9fa;
    padding: 6rem 0 4rem;
    text-align: center;
}

.project-header h1 {
    font-size: 3rem;
    margin-bottom: 1.5rem;
}

.project-meta {
    display: flex;
    justify-content: center;
    gap: 2rem;
    font-size: 1.1rem;
    color: #666;
}

.project-gallery {
    padding: 4rem 0;
}

.image-grid-main, .image-grid-technical {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.image-item {
    position: relative;
    overflow: hidden;
    border: 1px solid #eee;
}

.image-item img {
    width: 100%;
    height: 250px;
    object-fit: cover;
    display: block;
    transition: transform 0.3s ease;
}

.image-item:hover img {
    transform: scale(1.05);
}

.image-caption {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(0,0,0,0.7);
    color: #fff;
    padding: 0.75rem;
    font-size: 0.9rem;
    text-align: center;
}

.technical-section {
    margin: 4rem 0;
}

.technical-section h2 {
    font-size: 2rem;
    margin-bottom: 2rem;
    text-align: center;
}

.project-description {
    padding: 4rem 0;
}

.description-content {
    font-size: 1.1rem;
    line-height: 1.8;
    color: #444;
}

/* About page */
.about-header {
    text-align: center;
    padding: 4rem 0 2rem;
}

.about-header h1 {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
}

.about-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: start;
    margin: 4rem 0;
}

.about-text h2 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
}

.about-text p {
    margin-bottom: 1.5rem;
}

.about-image img {
    width: 100%;
    height: auto;
    display: block;
    border: 1px solid #eee;
}

/* Contact page */
.contact-header {
    text-align: center;
    padding: 4rem 0 2rem;
}

.contact-header h1 {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
}

.contact-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    margin: 4rem 0;
}

.contact-form {
    background-color: #f8f9fa;
    padding: 2.5rem;
    border: 1px solid #eee;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 0;
    font-family: inherit;
    font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #0066cc;
}

.contact-info h2 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
}

.contact-info p {
    line-height: 1.8;
    color: #666;
}

/* Footer */
footer {
    background-color: #f8f9fa;
    border-top: 1px solid #eee;
    text-align: center;
    padding: 2rem 0;
    font-size: 0.9rem;
    color: #666;
}

/* Responsive design */
@media (max-width: 768px) {
    .hero-content h1 {
        font-size: 2.5rem;
    }
    
    .hero-content p {
        font-size: 1.25rem;
    }
    
    .nav-links {
        display: none;
    }
    
    .about-content {
        grid-template-columns: 1fr;
    }
    
    .contact-content {
        grid-template-columns: 1fr;
    }
    
    .projects-grid {
        grid-template-columns: 1fr;
    }
    
    .page-header h1 {
        font-size: 2rem;
    }
    
    .project-header h1 {
        font-size: 2.25rem;
    }
}

@media (max-width: 480px) {
    .hero-content h1 {
        font-size: 2rem;
    }
    
    .hero-content p {
        font-size: 1.1rem;
    }
    
    .page-header h1 {
        font-size: 1.75rem;
    }
}
```

- [ ] **Step 2: Create main JavaScript file**

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle (if implemented in future)
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add any interactive features here
    console.log('Architect Portfolio JS loaded');
});
```

- [ ] **Step 3: Create placeholder image directory and note**

```bash
# Create directories for static files
mkdir -p app/static/images
mkdir -p app/static/uploads

# Note: In a real implementation, you would add actual placeholder images here
# For now, we'll create a simple note file
echo "Placeholder images should be added to app/static/images/" > app/static/images/README.txt
echo "Uploaded images will be stored in app/static/uploads/" > app/static/uploads/README.txt
```

- [ ] **Step 4: Commit static files and styling**

```bash
git add app/static/css/style.css app/static/js/main.js app/static/images/README.txt app/static/uploads/README.txt
git commit -m "feat: add andre tavares.net inspired CSS styling and static files setup"
```