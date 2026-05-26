# Bilingual Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add English/Portuguese language switching to the portfolio website with cookie-based persistence and side-by-side admin editing.

**Architecture:** Database column duplication (`_pt`/`_en` suffixes), JSON files for static UI text, Jinja2 helper functions for translation lookup, cookie-based language preference.

**Tech Stack:** FastAPI, SQLAlchemy, Jinja2, SQLite

---

## File Structure

**New Files:**
- `app/utils/i18n.py` - Translation helper functions
- `app/translations/en.json` - English static text
- `app/translations/pt.json` - Portuguese static text
- `app/migrations/add_i18n_columns.py` - Database migration script

**Modified Files:**
- `app/models/portfolio.py` - Add `_pt`/`_en` columns
- `app/models/setting.py` - Add `_pt`/`_en` columns to HeroImage
- `app/models/image.py` - Add `_pt`/`_en` columns
- `app/main.py` - Language routes, Jinja2 helpers, update POST handlers
- `app/templates/base.html` - Language switcher
- `app/templates/index.html` - Use translation functions
- `app/templates/portfolio.html` - Use translation functions
- `app/templates/portfolio_detail.html` - Use translation functions
- `app/templates/about.html` - Use translation functions
- `app/templates/contact.html` - Use translation functions
- `app/templates/admin/project_form.html` - Side-by-side fields
- `app/templates/admin/settings.html` - Side-by-side fields
- `app/static/css/style.css` - Language switcher styles
- `app/static/css/admin.css` - Bilingual form styles
- `seed/seed_data.py` - Add bilingual seed data

---

## Task 1: Create Translation Helper Functions

**Files:**
- Create: `app/utils/i18n.py`

- [ ] **Step 1: Create i18n utils file with language detection**

```python
import json
from pathlib import Path
from typing import Any
from fastapi import Request

_translations = {}

def get_current_language(request: Request) -> str:
    """
    Determine current language from cookie or Accept-Language header.
    
    Priority:
    1. Cookie 'lang'
    2. Accept-Language header
    3. Default to 'pt'
    
    Returns: 'pt' or 'en'
    """
    # Check cookie first
    lang = request.cookies.get('lang')
    if lang in ('pt', 'en'):
        return lang
    
    # Check Accept-Language header
    accept_lang = request.headers.get('accept-language', '')
    if 'en' in accept_lang.lower() and 'pt' not in accept_lang.lower():
        return 'en'
    
    # Default to Portuguese
    return 'pt'
```

- [ ] **Step 2: Add translation file loading function**

```python
def load_translations(lang: str) -> dict:
    """
    Load translation JSON file and cache in memory.
    
    Args:
        lang: Language code ('pt' or 'en')
    
    Returns: Translation dictionary
    """
    global _translations
    
    if lang in _translations:
        return _translations[lang]
    
    translations_path = Path(__file__).parent.parent / 'translations' / f'{lang}.json'
    
    if not translations_path.exists():
        return {}
    
    with open(translations_path, 'r', encoding='utf-8') as f:
        _translations[lang] = json.load(f)
    
    return _translations[lang]
```

- [ ] **Step 3: Add static text translation function**

```python
def t(key: str, lang: str) -> str:
    """
    Get static translation from JSON files.
    
    Args:
        key: Dot-notation key (e.g., 'nav.about')
        lang: Language code ('pt' or 'en')
    
    Returns: Translated string
    
    Fallback: pt.json -> key itself
    """
    translations = load_translations(lang)
    
    # Navigate nested dict using dot notation
    keys = key.split('.')
    value = translations
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Try Portuguese fallback
            if lang != 'pt':
                pt_translations = load_translations('pt')
                value = pt_translations
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return key  # Return key if not found
            else:
                return key
    
    return str(value) if value else key
```

- [ ] **Step 4: Add database field translation function**

```python
def get_translated_field(obj: Any, field_base: str, lang: str) -> str:
    """
    Get translated field from database object with fallback.
    
    Args:
        obj: Database model instance
        field_base: Base field name (e.g., 'name')
        lang: Language code ('pt' or 'en')
    
    Returns: Translated value
    
    Fallback order:
    1. {field_base}_{lang} (e.g., name_en)
    2. {field_base}_pt (Portuguese default)
    3. {field_base}_en (English fallback)
    4. Empty string
    """
    if obj is None:
        return ""
    
    # Try requested language
    field_name = f"{field_base}_{lang}"
    value = getattr(obj, field_name, None)
    if value:
        return value
    
    # Try Portuguese fallback
    if lang != 'pt':
        value = getattr(obj, f"{field_base}_pt", None)
        if value:
            return value
    
    # Try English fallback
    if lang != 'en':
        value = getattr(obj, f"{field_base}_en", None)
        if value:
            return value
    
    return ""
```

- [ ] **Step 5: Commit translation helpers**

```bash
git add app/utils/i18n.py
git commit -m "feat: add i18n translation helper functions"
```

---

## Task 2: Create Translation JSON Files

**Files:**
- Create: `app/translations/en.json`
- Create: `app/translations/pt.json`

- [ ] **Step 1: Create translations directory**

```bash
mkdir -p app/translations
```

- [ ] **Step 2: Create English translations file**

```json
{
  "nav": {
    "about": "About",
    "portfolio": "Portfolio",
    "contact": "Contact"
  },
  "buttons": {
    "send_message": "Send Message",
    "featured": "Featured",
    "save": "Save",
    "upload": "Upload",
    "remove": "Remove",
    "edit": "Edit",
    "delete": "Delete",
    "create": "Create"
  },
  "contact": {
    "heading": "Get in Touch",
    "name_label": "Name",
    "email_label": "Email",
    "message_label": "Message",
    "phone_label": "Phone",
    "address_label": "Address",
    "success": "Message sent successfully!"
  },
  "portfolio": {
    "heading": "Portfolio",
    "year": "Year",
    "location": "Location",
    "technical": "Technical Drawings"
  },
  "about": {
    "heading": "About"
  },
  "admin": {
    "english": "English",
    "portuguese": "Português"
  }
}
```

Save to: `app/translations/en.json`

- [ ] **Step 3: Create Portuguese translations file**

```json
{
  "nav": {
    "about": "Sobre",
    "portfolio": "Portfólio",
    "contact": "Contato"
  },
  "buttons": {
    "send_message": "Enviar Mensagem",
    "featured": "Destaque",
    "save": "Salvar",
    "upload": "Carregar",
    "remove": "Remover",
    "edit": "Editar",
    "delete": "Excluir",
    "create": "Criar"
  },
  "contact": {
    "heading": "Entre em Contato",
    "name_label": "Nome",
    "email_label": "Email",
    "message_label": "Mensagem",
    "phone_label": "Telefone",
    "address_label": "Endereço",
    "success": "Mensagem enviada com sucesso!"
  },
  "portfolio": {
    "heading": "Portfólio",
    "year": "Ano",
    "location": "Localização",
    "technical": "Desenhos Técnicos"
  },
  "about": {
    "heading": "Sobre"
  },
  "admin": {
    "english": "English",
    "portuguese": "Português"
  }
}
```

Save to: `app/translations/pt.json`

- [ ] **Step 4: Commit translation files**

```bash
git add app/translations/
git commit -m "feat: add EN/PT translation JSON files"
```

---

## Task 3: Update Database Models

**Files:**
- Modify: `app/models/portfolio.py`
- Modify: `app/models/setting.py`
- Modify: `app/models/image.py`

- [ ] **Step 1: Add i18n columns to Portfolio model**

Add these columns to the Portfolio class in `app/models/portfolio.py`:

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

class Portfolio(Base):
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Original columns (keep for backward compatibility)
    name = Column(String(255))
    description = Column(Text)
    location = Column(String(255))
    
    # Portuguese columns
    name_pt = Column(String(255))
    description_pt = Column(Text)
    location_pt = Column(String(255))
    
    # English columns
    name_en = Column(String(255))
    description_en = Column(Text)
    location_en = Column(String(255))
    
    year = Column(Integer)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

- [ ] **Step 2: Add i18n columns to HeroImage model**

Add these columns to the HeroImage class in `app/models/setting.py`:

```python
class HeroImage(Base):
    __tablename__ = "hero_images"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(500), nullable=False)
    
    # Original column (keep for backward compatibility)
    caption = Column(String(255))
    
    # Portuguese column
    caption_pt = Column(String(255))
    
    # English column
    caption_en = Column(String(255))
    
    sort_order = Column(Integer, default=0)
```

- [ ] **Step 3: Add i18n columns to PortfolioImage model**

Add these columns to the PortfolioImage class in `app/models/image.py`:

```python
class PortfolioImage(Base):
    __tablename__ = "portfolio_images"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id"))
    image_url = Column(String(500), nullable=False)
    
    # Original column (keep for backward compatibility)
    caption = Column(String(255))
    
    # Portuguese column
    caption_pt = Column(String(255))
    
    # English column
    caption_en = Column(String(255))
    
    is_cover = Column(Boolean, default=False)
    is_technical = Column(Boolean, default=False)
    created_at = Column(DateTime)
```

- [ ] **Step 4: Add i18n columns to TechnicalImage model**

Add these columns to the TechnicalImage class in `app/models/image.py` (if it exists as a separate model, otherwise skip):

```python
class TechnicalImage(Base):
    __tablename__ = "technical_images"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id"))
    image_url = Column(String(500), nullable=False)
    
    # Original column (keep for backward compatibility)
    caption = Column(String(255))
    
    # Portuguese column
    caption_pt = Column(String(255))
    
    # English column
    caption_en = Column(String(255))
    
    created_at = Column(DateTime)
```

- [ ] **Step 5: Commit model updates**

```bash
git add app/models/portfolio.py app/models/setting.py app/models/image.py
git commit -m "feat: add i18n columns to database models"
```

---

## Task 4: Create Database Migration Script

**Files:**
- Create: `app/migrations/add_i18n_columns.py`

- [ ] **Step 1: Create migrations directory**

```bash
mkdir -p app/migrations
```

- [ ] **Step 2: Create migration script**

```python
"""
Migration script to add i18n columns and migrate existing data.
Run this script to update the database schema.
"""
import sqlite3
from pathlib import Path

def run_migration(db_path: str = "test.db"):
    """Run migration to add i18n columns and migrate data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting i18n migration...")
    
    # Add columns to portfolio table
    print("Adding columns to portfolio table...")
    try:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN name_pt VARCHAR(255)")
        cursor.execute("ALTER TABLE portfolio ADD COLUMN name_en VARCHAR(255)")
        cursor.execute("ALTER TABLE portfolio ADD COLUMN description_pt TEXT")
        cursor.execute("ALTER TABLE portfolio ADD COLUMN description_en TEXT")
        cursor.execute("ALTER TABLE portfolio ADD COLUMN location_pt VARCHAR(255)")
        cursor.execute("ALTER TABLE portfolio ADD COLUMN location_en VARCHAR(255)")
        print("✓ Portfolio columns added")
    except sqlite3.OperationalError as e:
        print(f"Portfolio columns may already exist: {e}")
    
    # Add columns to hero_images table
    print("Adding columns to hero_images table...")
    try:
        cursor.execute("ALTER TABLE hero_images ADD COLUMN caption_pt VARCHAR(255)")
        cursor.execute("ALTER TABLE hero_images ADD COLUMN caption_en VARCHAR(255)")
        print("✓ HeroImage columns added")
    except sqlite3.OperationalError as e:
        print(f"HeroImage columns may already exist: {e}")
    
    # Add columns to portfolio_images table
    print("Adding columns to portfolio_images table...")
    try:
        cursor.execute("ALTER TABLE portfolio_images ADD COLUMN caption_pt VARCHAR(255)")
        cursor.execute("ALTER TABLE portfolio_images ADD COLUMN caption_en VARCHAR(255)")
        print("✓ PortfolioImage columns added")
    except sqlite3.OperationalError as e:
        print(f"PortfolioImage columns may already exist: {e}")
    
    # Migrate existing data to _pt columns
    print("Migrating existing data to Portuguese columns...")
    cursor.execute("""
        UPDATE portfolio 
        SET name_pt = name,
            description_pt = description,
            location_pt = location
        WHERE name_pt IS NULL
    """)
    
    cursor.execute("""
        UPDATE hero_images 
        SET caption_pt = caption
        WHERE caption_pt IS NULL
    """)
    
    cursor.execute("""
        UPDATE portfolio_images 
        SET caption_pt = caption
        WHERE caption_pt IS NULL
    """)
    
    # Add new site_settings keys for i18n
    print("Adding i18n site_settings keys...")
    
    # Get current values
    cursor.execute("SELECT key, value FROM site_settings")
    current_settings = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Create _pt keys from existing single-language keys
    keys_to_migrate = [
        'site_name', 'copyright', 'tagline', 
        'contact_blurb', 'about_title', 'about_body'
    ]
    
    for key in keys_to_migrate:
        if key in current_settings:
            pt_key = f"{key}_pt"
            en_key = f"{key}_en"
            
            # Add _pt key with existing value
            if pt_key not in current_settings:
                cursor.execute(
                    "INSERT INTO site_settings (key, value) VALUES (?, ?)",
                    (pt_key, current_settings[key])
                )
            
            # Add empty _en key
            if en_key not in current_settings:
                cursor.execute(
                    "INSERT INTO site_settings (key, value) VALUES (?, ?)",
                    (en_key, "")
                )
    
    conn.commit()
    print("✓ Data migration complete")
    
    conn.close()
    print("Migration finished successfully!")

if __name__ == "__main__":
    run_migration()
```

Save to: `app/migrations/add_i18n_columns.py`

- [ ] **Step 3: Run migration script**

```bash
python app/migrations/add_i18n_columns.py
```

Expected output:
```
Starting i18n migration...
Adding columns to portfolio table...
✓ Portfolio columns added
Adding columns to hero_images table...
✓ HeroImage columns added
Adding columns to portfolio_images table...
✓ PortfolioImage columns added
Migrating existing data to Portuguese columns...
Adding i18n site_settings keys...
✓ Data migration complete
Migration finished successfully!
```

- [ ] **Step 4: Verify migration worked**

```bash
sqlite3 test.db "SELECT name, name_pt, name_en FROM portfolio LIMIT 1;"
```

Expected: Should show existing name copied to name_pt, name_en is NULL/empty

- [ ] **Step 5: Commit migration script**

```bash
git add app/migrations/add_i18n_columns.py
git commit -m "feat: add database migration script for i18n"
```

---

## Task 5: Add Language Routes and Middleware

**Files:**
- Modify: `app/main.py`

- [ ] **Step 1: Import i18n helpers at top of main.py**

Add these imports after existing imports:

```python
from app.utils.i18n import get_current_language, t, get_translated_field
from fastapi.responses import RedirectResponse
```

- [ ] **Step 2: Register Jinja2 global functions**

Add this code after the `templates = Jinja2Templates(directory="app/templates")` line:

```python
# Register i18n helpers as Jinja2 globals
templates.env.globals['t'] = t
templates.env.globals['get_translated_field'] = get_translated_field
```

- [ ] **Step 3: Add language switching route**

Add this route before the existing routes:

```python
@app.get("/set-language")
async def set_language(
    request: Request,
    lang: str,
    redirect: str = None
):
    """
    Set language cookie and redirect back.
    
    Query params:
        lang: 'pt' or 'en'
        redirect: URL to redirect to (default: referrer or '/')
    """
    # Validate language
    if lang not in ('pt', 'en'):
        lang = 'pt'
    
    # Determine redirect URL
    redirect_url = redirect or request.headers.get('referer', '/')
    
    # Create response with cookie
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(
        key='lang',
        value=lang,
        max_age=365 * 24 * 60 * 60,  # 365 days
        path='/',
        samesite='lax'
    )
    
    return response
```

- [ ] **Step 4: Update existing routes to pass current_lang**

Find the index route and update it to include current_lang:

```python
@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    from app.models.portfolio import Portfolio
    from app.models.setting import HeroImage
    
    current_lang = get_current_language(request)
    settings = get_site_settings(db)
    featured_projects = db.query(Portfolio).filter(Portfolio.is_featured == True).all()
    hero_images = db.query(HeroImage).order_by(HeroImage.sort_order).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings,
        "featured_projects": featured_projects,
        "hero_images": hero_images,
        "current_lang": current_lang
    })
```

- [ ] **Step 5: Update portfolio list route**

```python
@app.get("/portfolio")
async def portfolio_list(request: Request, db: Session = Depends(get_db)):
    from app.models.portfolio import Portfolio
    
    current_lang = get_current_language(request)
    settings = get_site_settings(db)
    projects = db.query(Portfolio).order_by(Portfolio.year.desc()).all()
    
    return templates.TemplateResponse("portfolio.html", {
        "request": request,
        "settings": settings,
        "projects": projects,
        "current_lang": current_lang
    })
```

- [ ] **Step 6: Update portfolio detail route**

```python
@app.get("/portfolio/{project_id}")
async def portfolio_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    from app.models.portfolio import Portfolio
    from app.models.image import PortfolioImage
    
    current_lang = get_current_language(request)
    settings = get_site_settings(db)
    project = db.query(Portfolio).filter(Portfolio.id == project_id).first()
    
    if not project:
        return templates.TemplateResponse("404.html", {"request": request, "settings": settings}, status_code=404)
    
    images = db.query(PortfolioImage).filter(
        PortfolioImage.portfolio_id == project_id,
        PortfolioImage.is_technical == False
    ).all()
    
    technical = db.query(PortfolioImage).filter(
        PortfolioImage.portfolio_id == project_id,
        PortfolioImage.is_technical == True
    ).all()
    
    return templates.TemplateResponse("portfolio_detail.html", {
        "request": request,
        "settings": settings,
        "project": project,
        "images": images,
        "technical": technical,
        "current_lang": current_lang
    })
```

- [ ] **Step 7: Update about route**

```python
@app.get("/about")
async def about(request: Request, db: Session = Depends(get_db)):
    current_lang = get_current_language(request)
    settings = get_site_settings(db)
    
    return templates.TemplateResponse("about.html", {
        "request": request,
        "settings": settings,
        "current_lang": current_lang
    })
```

- [ ] **Step 8: Update contact route**

```python
@app.get("/contact")
async def contact(request: Request, db: Session = Depends(get_db)):
    current_lang = get_current_language(request)
    settings = get_site_settings(db)
    
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "settings": settings,
        "current_lang": current_lang
    })
```

- [ ] **Step 9: Commit route updates**

```bash
git add app/main.py
git commit -m "feat: add language switching routes and middleware"
```

---

## Task 6: Update Base Template with Language Switcher

**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/static/css/style.css`

- [ ] **Step 1: Add language switcher to navigation in base.html**

Find the `<ul class="nav-links">` section and update it:

```html
<ul class="nav-links">
    <li><a href="/about">{{ t('nav.about', current_lang) }}</a></li>
    <li><a href="/portfolio">{{ t('nav.portfolio', current_lang) }}</a></li>
    <li><a href="/contact">{{ t('nav.contact', current_lang) }}</a></li>
    <li class="lang-switcher">
        {% if current_lang == 'pt' %}
            <strong>PT</strong> | <a href="/set-language?lang=en">EN</a>
        {% else %}
            <a href="/set-language?lang=pt">PT</a> | <strong>EN</strong>
        {% endif %}
    </li>
</ul>
```

- [ ] **Step 2: Add language switcher styles to style.css**

Add these styles at the end of `app/static/css/style.css`:

```css
/* Language Switcher */
.lang-switcher {
    margin-left: 1rem;
    font-size: 0.875rem;
}

.lang-switcher strong {
    font-weight: 600;
    color: var(--text);
}

.lang-switcher a {
    opacity: 0.7;
    text-decoration: none;
    transition: opacity 0.2s;
}

.lang-switcher a:hover {
    opacity: 1;
}
```

- [ ] **Step 3: Test language switcher locally**

```bash
# Start server if not running
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 and verify:
- Language switcher appears in navigation
- Current language is bold
- Clicking switches language (check cookie in browser devtools)

- [ ] **Step 4: Commit base template and styles**

```bash
git add app/templates/base.html app/static/css/style.css
git commit -m "feat: add language switcher to navigation"
```

---

## Task 7: Update Public Templates with Translations

**Files:**
- Modify: `app/templates/index.html`
- Modify: `app/templates/portfolio.html`
- Modify: `app/templates/portfolio_detail.html`
- Modify: `app/templates/about.html`
- Modify: `app/templates/contact.html`

- [ ] **Step 1: Update index.html**

Replace hardcoded text with translation functions. Find and update:

```html
<!-- Featured projects section -->
<section class="portfolio-grid">
    <h2>{{ t('buttons.featured', current_lang) }}</h2>
    {% for project in featured_projects %}
    <article class="portfolio-card">
        <a href="/portfolio/{{ project.id }}">
            <!-- ... image ... -->
            <h3>{{ get_translated_field(project, 'name', current_lang) }}</h3>
            <p class="project-meta">
                {{ project.year }} — {{ get_translated_field(project, 'location', current_lang) }}
            </p>
        </a>
    </article>
    {% endfor %}
</section>
```

- [ ] **Step 2: Update portfolio.html**

Replace hardcoded text:

```html
<h1>{{ t('portfolio.heading', current_lang) }}</h1>

{% for project in projects %}
<article class="portfolio-card">
    <a href="/portfolio/{{ project.id }}">
        <!-- ... image ... -->
        <h3>{{ get_translated_field(project, 'name', current_lang) }}</h3>
        <p class="project-meta">
            {{ t('portfolio.year', current_lang) }}: {{ project.year }} — 
            {{ t('portfolio.location', current_lang) }}: {{ get_translated_field(project, 'location', current_lang) }}
        </p>
    </a>
</article>
{% endfor %}
```

- [ ] **Step 3: Update portfolio_detail.html**

Replace hardcoded text:

```html
<h1>{{ get_translated_field(project, 'name', current_lang) }}</h1>
<p class="project-meta">
    {{ t('portfolio.year', current_lang) }}: {{ project.year }} — 
    {{ t('portfolio.location', current_lang) }}: {{ get_translated_field(project, 'location', current_lang) }}
</p>
<div class="project-description">
    {{ get_translated_field(project, 'description', current_lang) }}
</div>

<!-- Images section -->
{% for image in images %}
<figure>
    <img src="{{ image.image_url }}" alt="{{ get_translated_field(image, 'caption', current_lang) }}">
    {% if image.caption_pt or image.caption_en %}
    <figcaption>{{ get_translated_field(image, 'caption', current_lang) }}</figcaption>
    {% endif %}
</figure>
{% endfor %}

<!-- Technical drawings section -->
{% if technical %}
<h2>{{ t('portfolio.technical', current_lang) }}</h2>
{% for image in technical %}
<figure>
    <img src="{{ image.image_url }}" alt="{{ get_translated_field(image, 'caption', current_lang) }}">
    {% if image.caption_pt or image.caption_en %}
    <figcaption>{{ get_translated_field(image, 'caption', current_lang) }}</figcaption>
    {% endif %}
</figure>
{% endfor %}
{% endif %}
```

- [ ] **Step 4: Update about.html**

Replace hardcoded text:

```html
<h1>{{ t('about.heading', current_lang) }}</h1>
<h2>{{ settings.get('about_title_' + current_lang, settings.get('about_title_pt', '')) }}</h2>
<div class="about-body">
    {{ settings.get('about_body_' + current_lang, settings.get('about_body_pt', '')) }}
</div>
```

- [ ] **Step 5: Update contact.html**

Replace hardcoded text:

```html
<h1>{{ t('contact.heading', current_lang) }}</h1>

<form method="POST" action="/contact">
    <label for="name">{{ t('contact.name_label', current_lang) }}</label>
    <input type="text" id="name" name="name" required>
    
    <label for="email">{{ t('contact.email_label', current_lang) }}</label>
    <input type="email" id="email" name="email" required>
    
    <label for="message">{{ t('contact.message_label', current_lang) }}</label>
    <textarea id="message" name="message" required></textarea>
    
    <button type="submit">{{ t('buttons.send_message', current_lang) }}</button>
</form>

{% if success %}
<p class="success-message">{{ t('contact.success', current_lang) }}</p>
{% endif %}

<div class="contact-info">
    <h2>{{ t('contact.heading', current_lang) }}</h2>
    <p>{{ t('contact.email_label', current_lang) }}: {{ settings.get('contact_email', '') }}</p>
    <p>{{ t('contact.phone_label', current_lang) }}: {{ settings.get('contact_phone', '') }}</p>
    <p>{{ t('contact.address_label', current_lang) }}: {{ settings.get('contact_address', '') }}</p>
</div>
```

- [ ] **Step 6: Test all public pages**

Visit each page and verify translations work:
- http://localhost:8000/ (index)
- http://localhost:8000/portfolio (list)
- http://localhost:8000/portfolio/1 (detail)
- http://localhost:8000/about
- http://localhost:8000/contact

Switch between PT/EN and verify content changes.

- [ ] **Step 7: Commit template updates**

```bash
git add app/templates/index.html app/templates/portfolio.html app/templates/portfolio_detail.html app/templates/about.html app/templates/contact.html
git commit -m "feat: add i18n support to public templates"
```

---

## Task 8: Update Admin Project Form

**Files:**
- Modify: `app/templates/admin/project_form.html`
- Modify: `app/static/css/admin.css`
- Modify: `app/main.py` (POST handlers)

- [ ] **Step 1: Add bilingual field styles to admin.css**

Add these styles to `app/static/css/admin.css`:

```css
/* Bilingual Form Fields */
.bilingual-field {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.bilingual-field .field-label {
    grid-column: 1 / -1;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.bilingual-field .lang-column {
    display: flex;
    flex-direction: column;
}

.bilingual-field .lang-column label {
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
    opacity: 0.7;
}

.bilingual-field input,
.bilingual-field textarea {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--line);
    background: var(--bg);
    font-size: 0.875rem;
    font-family: inherit;
}

.bilingual-field textarea {
    min-height: 8rem;
    resize: vertical;
}

@media (max-width: 768px) {
    .bilingual-field {
        grid-template-columns: 1fr;
    }
}
```

- [ ] **Step 2: Update project form with bilingual fields**

Replace the form fields in `app/templates/admin/project_form.html`:

```html
<form method="POST" enctype="multipart/form-data">
    <!-- Name field -->
    <div class="bilingual-field">
        <div class="field-label">Project Name</div>
        <div class="lang-column">
            <label>English</label>
            <input type="text" name="name_en" value="{{ project.name_en if project else '' }}">
        </div>
        <div class="lang-column">
            <label>Português</label>
            <input type="text" name="name_pt" value="{{ project.name_pt if project else '' }}" required>
        </div>
    </div>
    
    <!-- Description field -->
    <div class="bilingual-field">
        <div class="field-label">Description</div>
        <div class="lang-column">
            <label>English</label>
            <textarea name="description_en">{{ project.description_en if project else '' }}</textarea>
        </div>
        <div class="lang-column">
            <label>Português</label>
            <textarea name="description_pt" required>{{ project.description_pt if project else '' }}</textarea>
        </div>
    </div>
    
    <!-- Location field -->
    <div class="bilingual-field">
        <div class="field-label">Location</div>
        <div class="lang-column">
            <label>English</label>
            <input type="text" name="location_en" value="{{ project.location_en if project else '' }}">
        </div>
        <div class="lang-column">
            <label>Português</label>
            <input type="text" name="location_pt" value="{{ project.location_pt if project else '' }}">
        </div>
    </div>
    
    <!-- Year field (not translated) -->
    <div class="form-group">
        <label>Year</label>
        <input type="number" name="year" value="{{ project.year if project else '' }}" required>
    </div>
    
    <!-- Featured checkbox -->
    <div class="form-group">
        <label>
            <input type="checkbox" name="is_featured" {% if project and project.is_featured %}checked{% endif %}>
            Featured
        </label>
    </div>
    
    <!-- Image captions will be handled in the image upload sections -->
    
    <button type="submit">Save Project</button>
</form>
```

- [ ] **Step 3: Update project create POST handler in main.py**

Find the `/admin/projects/create` POST handler and update it:

```python
@app.post("/admin/projects/create")
async def create_project(
    request: Request,
    name_pt: str = Form(...),
    name_en: str = Form(None),
    description_pt: str = Form(...),
    description_en: str = Form(None),
    location_pt: str = Form(None),
    location_en: str = Form(None),
    year: int = Form(...),
    is_featured: bool = Form(False),
    db: Session = Depends(get_db)
):
    from app.models.portfolio import Portfolio
    from datetime import datetime
    
    project = Portfolio(
        name_pt=name_pt,
        name_en=name_en or "",
        description_pt=description_pt,
        description_en=description_en or "",
        location_pt=location_pt or "",
        location_en=location_en or "",
        year=year,
        is_featured=is_featured,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return RedirectResponse(url=f"/admin/projects/{project.id}/edit", status_code=302)
```

- [ ] **Step 4: Update project edit POST handler**

Find the `/admin/projects/{project_id}/edit` POST handler and update it:

```python
@app.post("/admin/projects/{project_id}/edit")
async def update_project(
    request: Request,
    project_id: int,
    name_pt: str = Form(...),
    name_en: str = Form(None),
    description_pt: str = Form(...),
    description_en: str = Form(None),
    location_pt: str = Form(None),
    location_en: str = Form(None),
    year: int = Form(...),
    is_featured: bool = Form(False),
    db: Session = Depends(get_db)
):
    from app.models.portfolio import Portfolio
    from datetime import datetime
    
    project = db.query(Portfolio).filter(Portfolio.id == project_id).first()
    if not project:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    project.name_pt = name_pt
    project.name_en = name_en or ""
    project.description_pt = description_pt
    project.description_en = description_en or ""
    project.location_pt = location_pt or ""
    project.location_en = location_en or ""
    project.year = year
    project.is_featured = is_featured
    project.updated_at = datetime.now()
    
    db.commit()
    
    return RedirectResponse(url=f"/admin/projects/{project_id}/edit", status_code=302)
```

- [ ] **Step 5: Test admin project form**

1. Login to admin: http://localhost:8000/admin
2. Create new project with both PT and EN text
3. Verify both languages save correctly
4. Edit existing project and add English translations
5. View project on public site and switch languages

- [ ] **Step 6: Commit admin form updates**

```bash
git add app/templates/admin/project_form.html app/static/css/admin.css app/main.py
git commit -m "feat: add bilingual fields to admin project form"
```

---

## Task 9: Update Admin Settings Form

**Files:**
- Modify: `app/templates/admin/settings.html`
- Modify: `app/main.py` (POST handlers)

- [ ] **Step 1: Update site name settings form**

Find the site name form in `app/templates/admin/settings.html` and update:

```html
<section class="settings-section">
    <h2>Site Name & Copyright</h2>
    <form action="/admin/settings/site-name" method="POST">
        <div class="bilingual-field">
            <div class="field-label">Site Name</div>
            <div class="lang-column">
                <label>English</label>
                <input type="text" name="site_name_en" value="{{ settings.get('site_name_en', '') }}">
            </div>
            <div class="lang-column">
                <label>Português</label>
                <input type="text" name="site_name_pt" value="{{ settings.get('site_name_pt', 'Daniel Moura') }}" required>
            </div>
        </div>
        
        <div class="bilingual-field">
            <div class="field-label">Copyright</div>
            <div class="lang-column">
                <label>English</label>
                <input type="text" name="copyright_en" value="{{ settings.get('copyright_en', '') }}">
            </div>
            <div class="lang-column">
                <label>Português</label>
                <input type="text" name="copyright_pt" value="{{ settings.get('copyright_pt', '© 2026 Daniel Moura') }}" required>
            </div>
        </div>
        
        <button type="submit">Save</button>
    </form>
</section>
```

- [ ] **Step 2: Update tagline settings form**

```html
<section class="settings-section">
    <h2>Taglines</h2>
    <p class="settings-hint">One per line. They'll cycle on the front page.</p>
    <form action="/admin/settings/taglines" method="POST">
        <div class="bilingual-field">
            <div class="field-label">Taglines</div>
            <div class="lang-column">
                <label>English</label>
                <textarea name="tagline_en" rows="5">{{ settings.get('tagline_en', '') }}</textarea>
            </div>
            <div class="lang-column">
                <label>Português</label>
                <textarea name="tagline_pt" rows="5" required>{{ settings.get('tagline_pt', '') }}</textarea>
            </div>
        </div>
        <button type="submit">Save</button>
    </form>
</section>
```

- [ ] **Step 3: Update contact info settings form**

```html
<section class="settings-section">
    <h2>Contact Info</h2>
    <form action="/admin/settings/contact" method="POST">
        <!-- Non-translated fields -->
        <div class="form-group">
            <label>Email</label>
            <input type="email" name="contact_email" value="{{ settings.get('contact_email', '') }}">
        </div>
        <div class="form-group">
            <label>Phone</label>
            <input type="text" name="contact_phone" value="{{ settings.get('contact_phone', '') }}">
        </div>
        <div class="form-group">
            <label>Address</label>
            <textarea name="contact_address" rows="3">{{ settings.get('contact_address', '') }}</textarea>
        </div>
        
        <!-- Translated blurb -->
        <div class="bilingual-field">
            <div class="field-label">Contact Page Blurb</div>
            <div class="lang-column">
                <label>English</label>
                <textarea name="contact_blurb_en" rows="4">{{ settings.get('contact_blurb_en', '') }}</textarea>
            </div>
            <div class="lang-column">
                <label>Português</label>
                <textarea name="contact_blurb_pt" rows="4">{{ settings.get('contact_blurb_pt', '') }}</textarea>
            </div>
        </div>
        
        <button type="submit">Save</button>
    </form>
</section>
```

- [ ] **Step 4: Update about page settings form**

```html
<section class="settings-section">
    <h2>About Page</h2>
    <form action="/admin/settings/about" method="POST">
        <div class="bilingual-field">
            <div class="field-label">Title</div>
            <div class="lang-column">
                <label>English</label>
                <input type="text" name="about_title_en" value="{{ settings.get('about_title_en', '') }}">
            </div>
            <div class="lang-column">
                <label>Português</label>
                <input type="text" name="about_title_pt" value="{{ settings.get('about_title_pt', '') }}" required>
            </div>
        </div>
        
        <div class="bilingual-field">
            <div class="field-label">Body Text</div>
            <div class="lang-column">
                <label>English</label>
                <textarea name="about_body_en" rows="8">{{ settings.get('about_body_en', '') }}</textarea>
            </div>
            <div class="lang-column">
                <label>Português</label>
                <textarea name="about_body_pt" rows="8" required>{{ settings.get('about_body_pt', '') }}</textarea>
            </div>
        </div>
        
        <button type="submit">Save</button>
    </form>
</section>
```

- [ ] **Step 5: Update POST handlers in main.py**

Update the site name handler:

```python
@app.post("/admin/settings/site-name")
async def update_site_name(
    request: Request,
    site_name_pt: str = Form(...),
    site_name_en: str = Form(""),
    copyright_pt: str = Form(...),
    copyright_en: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    
    settings_to_update = {
        'site_name_pt': site_name_pt,
        'site_name_en': site_name_en,
        'copyright_pt': copyright_pt,
        'copyright_en': copyright_en
    }
    
    for key, value in settings_to_update.items():
        row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(SiteSetting(key=key, value=value))
    
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)
```

Update the taglines handler:

```python
@app.post("/admin/settings/taglines")
async def update_taglines(
    request: Request,
    tagline_pt: str = Form(...),
    tagline_en: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    
    for key, value in [('tagline_pt', tagline_pt), ('tagline_en', tagline_en)]:
        row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(SiteSetting(key=key, value=value))
    
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)
```

Update the contact handler:

```python
@app.post("/admin/settings/contact")
async def update_contact(
    request: Request,
    contact_email: str = Form(""),
    contact_phone: str = Form(""),
    contact_address: str = Form(""),
    contact_blurb_pt: str = Form(""),
    contact_blurb_en: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    
    settings_to_update = {
        'contact_email': contact_email,
        'contact_phone': contact_phone,
        'contact_address': contact_address,
        'contact_blurb_pt': contact_blurb_pt,
        'contact_blurb_en': contact_blurb_en
    }
    
    for key, value in settings_to_update.items():
        row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(SiteSetting(key=key, value=value))
    
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)
```

Update the about handler:

```python
@app.post("/admin/settings/about")
async def update_about(
    request: Request,
    about_title_pt: str = Form(...),
    about_title_en: str = Form(""),
    about_body_pt: str = Form(...),
    about_body_en: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.models.setting import SiteSetting
    
    settings_to_update = {
        'about_title_pt': about_title_pt,
        'about_title_en': about_title_en,
        'about_body_pt': about_body_pt,
        'about_body_en': about_body_en
    }
    
    for key, value in settings_to_update.items():
        row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(SiteSetting(key=key, value=value))
    
    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)
```

- [ ] **Step 6: Test admin settings forms**

1. Login to admin: http://localhost:8000/admin/settings
2. Update each settings section with both PT and EN text
3. Verify settings save correctly
4. View public pages and switch languages to verify

- [ ] **Step 7: Commit admin settings updates**

```bash
git add app/templates/admin/settings.html app/main.py
git commit -m "feat: add bilingual fields to admin settings forms"
```

---

## Task 10: Update Image Caption Forms

**Files:**
- Modify: Image upload sections in admin templates
- Modify: `app/main.py` (image upload handlers)

- [ ] **Step 1: Update hero image upload form in settings.html**

Find the hero images section and update the caption field:

```html
<form action="/admin/settings/hero" method="POST" enctype="multipart/form-data">
    <div class="form-group">
        <label>Image</label>
        <input type="file" name="file" accept="image/*" required>
    </div>
    
    <div class="bilingual-field">
        <div class="field-label">Caption</div>
        <div class="lang-column">
            <label>English</label>
            <input type="text" name="caption_en">
        </div>
        <div class="lang-column">
            <label>Português</label>
            <input type="text" name="caption_pt">
        </div>
    </div>
    
    <button type="submit">Upload Hero Image</button>
</form>
```

- [ ] **Step 2: Update hero image upload handler in main.py**

Find the `/admin/settings/hero` POST handler and update:

```python
@app.post("/admin/settings/hero")
async def upload_hero_image(
    request: Request,
    file: UploadFile = File(...),
    caption_pt: str = Form(""),
    caption_en: str = Form(""),
    db: Session = Depends(get_db)
):
    from app.models.setting import HeroImage
    import shutil
    from pathlib import Path
    
    # Save file
    upload_dir = Path("app/static/uploads/hero")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"hero-{int(time.time())}{ext}"
    filepath = upload_dir / filename
    
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Create hero image record
    hero = HeroImage(
        image_url=f"/static/uploads/hero/{filename}",
        caption_pt=caption_pt,
        caption_en=caption_en,
        sort_order=db.query(HeroImage).count()
    )
    
    db.add(hero)
    db.commit()
    
    return RedirectResponse(url="/admin/settings", status_code=302)
```

- [ ] **Step 3: Update portfolio image upload in project_form.html**

Find the image upload section and update:

```html
<div class="image-upload-section">
    <h3>Upload Images</h3>
    <form action="/admin/projects/{{ project.id }}/images" method="POST" enctype="multipart/form-data">
        <input type="file" name="file" accept="image/*" required>
        
        <div class="bilingual-field">
            <div class="field-label">Caption</div>
            <div class="lang-column">
                <label>English</label>
                <input type="text" name="caption_en">
            </div>
            <div class="lang-column">
                <label>Português</label>
                <input type="text" name="caption_pt">
            </div>
        </div>
        
        <label>
            <input type="checkbox" name="is_technical">
            Technical Drawing
        </label>
        
        <button type="submit">Upload</button>
    </form>
</div>
```

- [ ] **Step 4: Update portfolio image upload handler in main.py**

Find the image upload handler and update:

```python
@app.post("/admin/projects/{project_id}/images")
async def upload_project_image(
    request: Request,
    project_id: int,
    file: UploadFile = File(...),
    caption_pt: str = Form(""),
    caption_en: str = Form(""),
    is_technical: bool = Form(False),
    db: Session = Depends(get_db)
):
    from app.models.image import PortfolioImage
    import shutil
    from pathlib import Path
    import uuid
    
    # Save file
    upload_dir = Path(f"app/static/uploads/{project_id}")
    if is_technical:
        upload_dir = upload_dir / "technical"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = upload_dir / filename
    
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Create image record
    image_path = f"/static/uploads/{project_id}"
    if is_technical:
        image_path += "/technical"
    image_path += f"/{filename}"
    
    image = PortfolioImage(
        portfolio_id=project_id,
        image_url=image_path,
        caption_pt=caption_pt,
        caption_en=caption_en,
        is_technical=is_technical,
        is_cover=False,
        created_at=datetime.now()
    )
    
    db.add(image)
    db.commit()
    
    return RedirectResponse(url=f"/admin/projects/{project_id}/edit", status_code=302)
```

- [ ] **Step 5: Test image caption functionality**

1. Upload a new hero image with both PT and EN captions
2. Upload project images with captions
3. View on public site and switch languages to verify captions change

- [ ] **Step 6: Commit image caption updates**

```bash
git add app/templates/admin/settings.html app/templates/admin/project_form.html app/main.py
git commit -m "feat: add bilingual captions to image uploads"
```

---

## Task 11: Update Seed Data

**Files:**
- Modify: `seed/seed_data.py`

- [ ] **Step 1: Update seed data with bilingual content**

Find the portfolio seed data and update:

```python
portfolios = [
    {
        "name_pt": "Casa Minimalista",
        "name_en": "Minimalist House",
        "description_pt": "Uma residência contemporânea que celebra a simplicidade e a luz natural.",
        "description_en": "A contemporary residence that celebrates simplicity and natural light.",
        "location_pt": "Lisboa, Portugal",
        "location_en": "Lisbon, Portugal",
        "year": 2023,
        "is_featured": True
    },
    # ... add more projects with bilingual content
]

for project_data in portfolios:
    project = Portfolio(**project_data)
    project.created_at = datetime.now()
    project.updated_at = datetime.now()
    db.add(project)
```

Update site settings:

```python
site_settings = [
    {"key": "site_name_pt", "value": "Daniel Moura"},
    {"key": "site_name_en", "value": "Daniel Moura"},
    {"key": "copyright_pt", "value": "© 2026 Daniel Moura"},
    {"key": "copyright_en", "value": "© 2026 Daniel Moura"},
    {"key": "tagline_pt", "value": "Design is not only what we see, but what quietly transforms how we dwell."},
    {"key": "tagline_en", "value": "Design is not only what we see, but what quietly transforms how we dwell."},
    {"key": "about_title_pt", "value": "Sobre\nDaniel Moura"},
    {"key": "about_title_en", "value": "About\nDaniel Moura"},
    {"key": "about_body_pt", "value": "Design is not only what we see, but what quietly transforms how we dwell.\n\nDaniel Moura is an architecture practice with projects spanning residential, commercial, and cultural spaces."},
    {"key": "about_body_en", "value": "Design is not only what we see, but what quietly transforms how we dwell.\n\nDaniel Moura is an architecture practice with projects spanning residential, commercial, and cultural spaces."},
    {"key": "contact_blurb_pt", "value": "Adoraríamos ouvir de você. Se você tem um projeto em mente ou simplesmente quer saber mais sobre nosso estúdio, sinta-se à vontade para entrar em contato."},
    {"key": "contact_blurb_en", "value": "We would love to hear from you. Whether you have a project in mind or simply want to learn more about our studio, feel free to reach out."},
    {"key": "contact_email", "value": "dadamoura@cloud.com"},
    {"key": "contact_phone", "value": "+351 931 110 004"},
    {"key": "contact_address", "value": "Rua Augusta, 123\nLisbon, Portugal"},
    {"key": "logo_path", "value": "/static/logo.png"}
]

for setting in site_settings:
    db.add(SiteSetting(**setting))
```

- [ ] **Step 2: Test seed data**

```bash
# Backup existing database
cp test.db test.db.backup

# Run seed script
python seed/seed_data.py

# Verify bilingual content loaded
sqlite3 test.db "SELECT name_pt, name_en FROM portfolio LIMIT 1;"
```

- [ ] **Step 3: Commit seed data updates**

```bash
git add seed/seed_data.py
git commit -m "feat: update seed data with bilingual content"
```

---

## Task 12: Deploy to Server

**Files:**
- All files committed so far

- [ ] **Step 1: Push all changes to GitHub**

```bash
git push origin main
```

- [ ] **Step 2: SSH to server and pull changes**

```bash
ssh gustavo@10.169.110.116 "cd ~/docker-apps/dada-moura-portfolio && git pull origin main"
```

- [ ] **Step 3: Run migration on server**

```bash
ssh gustavo@10.169.110.116 "cd ~/docker-apps/dada-moura-portfolio && sudo docker compose exec app python app/migrations/add_i18n_columns.py"
```

Expected output showing migration completed successfully.

- [ ] **Step 4: Rebuild and restart Docker container**

```bash
ssh gustavo@10.169.110.116 "cd ~/docker-apps/dada-moura-portfolio && sudo docker compose up -d --build"
```

- [ ] **Step 5: Verify deployment**

Visit http://10.169.110.116:8088 and verify:
- Language switcher appears in navigation
- Can switch between PT and EN
- Content changes when switching languages
- Admin forms show bilingual fields

- [ ] **Step 6: Test on server**

1. Switch to English, verify translation
2. Switch to Portuguese, verify translation
3. Login to admin and add English translations to a project
4. View project on public site in both languages
5. Check cookie persistence (refresh page, language should stay)

- [ ] **Step 7: Create deployment tag**

```bash
git tag -a v1.1.0-bilingual -m "Release: Bilingual support (EN/PT)"
git push origin v1.1.0-bilingual
```

---

## Testing Checklist

After completing all tasks, verify:

**Language Detection:**
- [ ] Cookie `lang=pt` shows Portuguese
- [ ] Cookie `lang=en` shows English
- [ ] No cookie defaults to Portuguese
- [ ] Language persists across page loads

**Language Switching:**
- [ ] PT/EN links appear in navigation
- [ ] Current language is bold
- [ ] Clicking switches language
- [ ] Cookie set correctly

**Public Pages:**
- [ ] Home page translates
- [ ] Portfolio list translates
- [ ] Portfolio detail translates
- [ ] About page translates
- [ ] Contact page translates
- [ ] Navigation translates
- [ ] Buttons translate
- [ ] Form labels translate

**Admin Panel:**
- [ ] Project form shows side-by-side fields
- [ ] Settings forms show side-by-side fields
- [ ] Can create project with both languages
- [ ] Can edit project and add translations
- [ ] Image captions have both languages
- [ ] Portuguese is required, English is optional

**Fallback:**
- [ ] Portuguese content + no English → shows Portuguese
- [ ] English content + no Portuguese → shows English
- [ ] Missing translation falls back gracefully

**Performance:**
- [ ] Page load time unchanged
- [ ] No N+1 query issues
- [ ] Translation JSON cached in memory

---

## Rollback Plan

If issues occur:

**Quick rollback (hide feature):**
```css
/* Add to style.css */
.lang-switcher { display: none; }
```

**Full rollback:**
```bash
git revert HEAD~12..HEAD
git push origin main
# Deploy via GitHub Actions or manual SSH
```

Database is safe - old columns still exist, can revert templates to use them.
