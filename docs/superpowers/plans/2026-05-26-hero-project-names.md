# Hero Images with Project Names Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Display project names at top-center of main page that update automatically as the hero slideshow advances

**Architecture:** Extend HeroImage model with portfolio_id foreign key, remove standalone hero upload UI, update frontend to show project name with smooth transitions, and eager-load portfolio data in backend routes.

**Tech Stack:** FastAPI, SQLAlchemy, Jinja2, vanilla JavaScript, CSS

---

## File Structure

### Files to Create
- Database migration script (inline in task steps, no separate file)

### Files to Modify
- `app/models/setting.py` - Add portfolio_id column and relationship to HeroImage
- `app/core/settings_helper.py` - Eager-load portfolio relationship
- `app/main.py` - Update add_hero_from_project endpoint, remove upload_hero_image endpoint
- `app/templates/admin/settings.html` - Remove standalone hero upload form
- `app/templates/index.html` - Add project name display element and update JavaScript
- `app/static/css/style.css` - Add styling for project name display

---

## Task 1: Add portfolio_id to HeroImage Model

**Files:**
- Modify: `app/models/setting.py:13-23`

- [ ] **Step 1: Add portfolio_id column and relationship to HeroImage model**

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
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
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    # Legacy single-language caption (keep for backward compatibility)
    caption = Column(String(255), nullable=True)
    # Bilingual captions
    caption_pt = Column(String(255), nullable=True)
    caption_en = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    
    portfolio = relationship("Portfolio", backref="hero_images")
```

- [ ] **Step 2: Run database migration to add column**

Run the following Python script to add the portfolio_id column:

```bash
python -c "
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE hero_images ADD COLUMN portfolio_id INTEGER'))
    conn.commit()
print('Migration complete: Added portfolio_id to hero_images')
"
```

Expected output: `Migration complete: Added portfolio_id to hero_images`

- [ ] **Step 3: Verify model works with test query**

```bash
python -c "
from app.db.session import SessionLocal
from app.models.setting import HeroImage

db = SessionLocal()
heroes = db.query(HeroImage).all()
print(f'Found {len(heroes)} hero images')
for h in heroes:
    print(f'  - {h.image_url}, portfolio_id={h.portfolio_id}')
db.close()
"
```

Expected: List of hero images with portfolio_id showing None (for existing images)

- [ ] **Step 4: Commit model changes**

```bash
git add app/models/setting.py
git commit -m "feat: add portfolio_id to HeroImage model"
```

---

## Task 2: Update Backend to Load Portfolio Data

**Files:**
- Modify: `app/core/settings_helper.py:1-13`
- Modify: `app/main.py:59-83` (home route)
- Modify: `app/main.py:284-304` (admin_settings route)

- [ ] **Step 1: Update settings_helper to eager-load portfolio relationship**

```python
from app.db.session import SessionLocal
from app.models.setting import SiteSetting, HeroImage
from sqlalchemy.orm import joinedload


def get_site_settings():
    db = SessionLocal()
    try:
        rows = db.query(SiteSetting).all()
        settings = {r.key: r.value for r in rows}
        settings["hero_images"] = db.query(HeroImage).options(joinedload(HeroImage.portfolio)).order_by(HeroImage.sort_order).all()
        return settings
    finally:
        db.close()
```

- [ ] **Step 2: Update home route to pass portfolio data with hero images**

Find the home route (around line 59) and update it:

```python
@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request, 
    db: Session = Depends(get_db), 
    lang: Optional[str] = Query(default=None),
    language: Optional[str] = Cookie(default="pt")
):
    from app.crud import portfolio as crud_portfolio
    from app.models.image import PortfolioImage
    # Prioritize query param over cookie
    selected_lang = validate_language(lang) if lang else validate_language(language)
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
        "lang": selected_lang,
    })
```

Note: The home route already uses `get_site_settings()` which now includes portfolio data, so this step is verification only.

- [ ] **Step 3: Update admin_settings route to load portfolio data with project images**

Find the admin_settings route (around line 284) and update it:

```python
@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, db: Session = Depends(get_db)):
    from app.models.setting import SiteSetting, HeroImage
    from app.models.image import PortfolioImage, TechnicalImage
    from app.models.portfolio import Portfolio
    from sqlalchemy.orm import joinedload
    
    settings_list = {r.key: r.value for r in db.query(SiteSetting).all()}
    hero_images = db.query(HeroImage).options(joinedload(HeroImage.portfolio)).order_by(HeroImage.sort_order).all()
    site_settings = get_site_settings()
    
    # Load all project images with their portfolio data
    portfolio_images = db.query(PortfolioImage).options(joinedload(PortfolioImage.portfolio)).all()
    technical_images = db.query(TechnicalImage).options(joinedload(TechnicalImage.portfolio)).all()
    project_images = portfolio_images + technical_images
    
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
```

- [ ] **Step 4: Test the updated routes**

```bash
# Start the server if not running
uvicorn app.main:app --reload &
sleep 3

# Test home page loads without errors
curl -s http://localhost:8000/ | grep -q "hero" && echo "Home page OK" || echo "Home page ERROR"

# Stop the test server
pkill -f "uvicorn app.main:app"
```

Expected: "Home page OK"

- [ ] **Step 5: Commit backend changes**

```bash
git add app/core/settings_helper.py app/main.py
git commit -m "feat: eager-load portfolio data for hero images"
```

---

## Task 3: Update add_hero_from_project Endpoint

**Files:**
- Modify: `app/main.py:422-431`

- [ ] **Step 1: Update add_hero_from_project to set portfolio_id**

Find the `add_hero_from_project` route (around line 422) and update it:

```python
@app.get("/admin/settings/hero/add-from-project")
async def add_hero_from_project(image_url: str, db: Session = Depends(get_db)):
    from app.models.setting import HeroImage
    from app.models.image import PortfolioImage, TechnicalImage
    from sqlalchemy import func as sa_func
    
    # Check if already exists
    existing = db.query(HeroImage).filter(HeroImage.image_url == image_url).first()
    if not existing:
        # Find the portfolio_id from the source image
        portfolio_id = None
        source_img = db.query(PortfolioImage).filter(PortfolioImage.image_url == image_url).first()
        if source_img:
            portfolio_id = source_img.portfolio_id
        else:
            source_img = db.query(TechnicalImage).filter(TechnicalImage.image_url == image_url).first()
            if source_img:
                portfolio_id = source_img.portfolio_id
        
        max_order = db.query(sa_func.max(HeroImage.sort_order)).scalar() or 0
        db.add(HeroImage(
            image_url=image_url,
            portfolio_id=portfolio_id,
            sort_order=max_order + 1
        ))
        db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)
```

- [ ] **Step 2: Test the endpoint with manual database query**

```bash
python -c "
from app.db.session import SessionLocal
from app.models.image import PortfolioImage

db = SessionLocal()
# Get first project image
img = db.query(PortfolioImage).first()
if img:
    print(f'Test image: {img.image_url}')
    print(f'Portfolio ID: {img.portfolio_id}')
else:
    print('No project images found')
db.close()
"
```

Expected: Output showing an image URL and its portfolio ID

- [ ] **Step 3: Commit endpoint changes**

```bash
git add app/main.py
git commit -m "feat: set portfolio_id when adding hero from project"
```

---

## Task 4: Remove Standalone Hero Upload

**Files:**
- Modify: `app/templates/admin/settings.html:81-97`
- Modify: `app/main.py:366-392`

- [ ] **Step 1: Remove upload form from admin settings template**

In `app/templates/admin/settings.html`, find lines 81-97 (the upload form section) and delete them:

```html
        <form action="/admin/settings/hero" method="POST" enctype="multipart/form-data" class="upload-form">
            <div class="form-group">
                <label for="hero_file">Add Hero Image</label>
                <input type="file" id="hero_file" name="file" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.75rem;">
                <div class="form-group">
                    <label for="caption_pt">Caption (PT)</label>
                    <input type="text" id="caption_pt" name="caption_pt">
                </div>
                <div class="form-group">
                    <label for="caption_en">Caption (EN)</label>
                    <input type="text" id="caption_en" name="caption_en">
                </div>
            </div>
            <button type="submit" class="btn-upload">Upload</button>
        </form>
```

Replace with: (nothing - just delete the entire form)

The section should now go directly from the current hero images display to the "From Projects" section.

- [ ] **Step 2: Comment out or remove upload_hero_image endpoint**

In `app/main.py`, find the `upload_hero_image` route (around line 366) and comment it out or delete it:

```python
# Disabled: Hero images must come from projects
# @app.post("/admin/settings/hero")
# async def upload_hero_image(
#     request: Request,
#     file: UploadFile = File(...),
#     caption_pt: str = Form(None),
#     caption_en: str = Form(None),
#     db: Session = Depends(get_db)
# ):
#     from app.models.setting import HeroImage
#     from sqlalchemy import func as sa_func
#     upload_dir = Path("app/static/uploads/hero")
#     upload_dir.mkdir(parents=True, exist_ok=True)
#     ext = Path(file.filename).suffix or ".jpg"
#     filename = f"hero_{uuid.uuid4().hex[:12]}{ext}"
#     filepath = upload_dir / filename
#     with open(filepath, "wb") as f:
#         shutil.copyfileobj(file.file, f)
#     max_order = db.query(sa_func.max(HeroImage.sort_order)).scalar() or 0
#     db.add(HeroImage(
#         image_url=f"/static/uploads/hero/{filename}",
#         caption_pt=caption_pt,
#         caption_en=caption_en,
#         caption=caption_pt,  # Legacy field
#         sort_order=max_order + 1
#     ))
#     db.commit()
#     return RedirectResponse(url="/admin/settings", status_code=302)
```

- [ ] **Step 3: Verify admin settings page loads without upload form**

```bash
# Start server
uvicorn app.main:app --reload &
sleep 3

# Test admin settings (requires auth, so just check it doesn't error)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/settings

# Stop server
pkill -f "uvicorn app.main:app"
```

Expected: Status code 200 or 307 (redirect to login)

- [ ] **Step 4: Commit removal changes**

```bash
git add app/templates/admin/settings.html app/main.py
git commit -m "feat: remove standalone hero upload, require project images"
```

---

## Task 5: Add Project Name Display to Frontend

**Files:**
- Modify: `app/templates/index.html:6-43`
- Modify: `app/static/css/style.css` (append at end)

- [ ] **Step 1: Add project name display element to index.html**

In `app/templates/index.html`, find the hero section (around line 6) and add the project name display:

```html
{% extends "base.html" %}

{% block title %}{{ settings.get('site_name', 'Daniel Moura') }}{% endblock %}

{% block content %}
<div id="hero-project-name" class="hero-project-name"></div>

<section class="hero">
    {% if settings.hero_images %}
    <div class="hero-slideshow">
        {% for img in settings.hero_images %}
        <img src="{{ img.image_url }}" 
             alt="{{ get_translated_field(img, 'caption', lang) or '' }}" 
             class="hero-image hero-slide{% if loop.first %} active{% endif %}"
             data-project-id="{{ img.portfolio_id or '' }}"
             data-project-name-pt="{{ img.portfolio.name_pt if img.portfolio else '' }}"
             data-project-name-en="{{ img.portfolio.name_en if img.portfolio else '' }}">
        {% endfor %}
    </div>
    {% else %}
    <img src="/static/uploads/hero-minimalist.jpg" alt="Architecture Studio" class="hero-image">
    {% endif %}
</section>

<div class="bottom-nav">
    <a href="/about" class="bottom-about">{{ t('nav.about', lang | default('pt')) }}</a>
</div>

<script>
(function() {
    var slides = document.querySelectorAll('.hero-slide');
    var sidx = 0;
    var nameEl = document.getElementById('hero-project-name');
    var currentLang = '{{ lang }}';

    function updateProjectName() {
        var slide = slides[sidx];
        var projectId = slide.getAttribute('data-project-id');
        var projectNamePt = slide.getAttribute('data-project-name-pt');
        var projectNameEn = slide.getAttribute('data-project-name-en');
        
        if (projectId && (projectNamePt || projectNameEn)) {
            var projectName = currentLang === 'en' ? projectNameEn : projectNamePt;
            // Fallback to other language if current is empty
            if (!projectName) {
                projectName = projectNamePt || projectNameEn;
            }
            nameEl.textContent = projectName;
            nameEl.style.opacity = '1';
        } else {
            nameEl.style.opacity = '0';
        }
    }

    function advance() {
        // Fade out name
        nameEl.style.opacity = '0';
        
        // Change slide after brief delay
        setTimeout(function() {
            slides[sidx].classList.remove('active');
            sidx = (sidx + 1) % slides.length;
            slides[sidx].classList.add('active');
            
            // Fade in new name after slide transition starts
            setTimeout(updateProjectName, 300);
        }, 300);
    }

    if (slides.length > 0) {
        // Initialize with first slide's project name
        updateProjectName();
    }

    if (slides.length > 1) {
        var hero = document.querySelector('.hero');
        hero.classList.add('hero-clickable');
        hero.addEventListener('click', advance);
        slides.forEach(function(s) {
            s.addEventListener('click', function(e) { e.stopPropagation(); advance(); });
        });
        setInterval(advance, 6000);
    }
})();
</script>
{% endblock %}
```

- [ ] **Step 2: Add CSS styling for project name display**

Add to the end of `app/static/css/style.css`:

```css
/* Hero project name display */
.hero-project-name {
    position: fixed;
    top: 2rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text);
    text-align: center;
    transition: opacity 0.5s ease;
    opacity: 0;
    pointer-events: none;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    max-width: 90%;
    line-height: 1.2;
}

@media (max-width: 768px) {
    .hero-project-name {
        font-size: 1rem;
        top: 1rem;
    }
}
```

- [ ] **Step 3: Test the frontend with the server**

```bash
# Start server
uvicorn app.main:app --reload &
sleep 3

# Open browser to test (manual step)
echo "Open http://localhost:8000/ and verify:"
echo "1. Project name appears at top center"
echo "2. Project name fades when clicking hero image"
echo "3. Project name updates to match new image"
echo "4. If hero image has no project, name disappears"

# Stop server after manual testing
pkill -f "uvicorn app.main:app"
```

- [ ] **Step 4: Commit frontend changes**

```bash
git add app/templates/index.html app/static/css/style.css
git commit -m "feat: display project name on hero slideshow"
```

---

## Task 6: End-to-End Testing

**Files:**
- None (testing only)

- [ ] **Step 1: Test adding hero image from project**

Manual test:
1. Start server: `uvicorn app.main:app --reload`
2. Log into admin at http://localhost:8000/admin/login
3. Go to Settings (http://localhost:8000/admin/settings)
4. Scroll to "From Projects" section
5. Click "+" on a project image
6. Verify image appears in "Hero Images" section
7. Go to home page (http://localhost:8000/)
8. Verify project name appears at top center

Expected: Project name displays correctly

- [ ] **Step 2: Test slideshow cycling**

Manual test:
1. Add 2-3 different project images as hero images
2. Go to home page
3. Click on hero image or wait 6 seconds
4. Verify project name fades out and new name fades in
5. Verify each hero image shows its correct project name

Expected: Smooth transitions, correct project names

- [ ] **Step 3: Test language switching**

Manual test:
1. On home page with project name showing
2. Switch language from PT to EN (or vice versa)
3. Verify project name updates to correct language

Expected: Project name displays in selected language

- [ ] **Step 4: Test legacy hero images (no project)**

Manual test:
1. If any old hero images exist without portfolio_id:
   - Verify they still display as images
   - Verify project name element is hidden (opacity: 0) when these display
2. If no legacy images exist, skip this test

Expected: Graceful degradation, no errors

- [ ] **Step 5: Test deleted project scenario**

Database test:
```bash
python -c "
from app.db.session import SessionLocal
from app.models.setting import HeroImage

db = SessionLocal()
# Find hero image with portfolio_id
hero = db.query(HeroImage).filter(HeroImage.portfolio_id.isnot(None)).first()
if hero:
    print(f'Hero image {hero.id} has portfolio_id={hero.portfolio_id}')
    if hero.portfolio:
        print(f'Portfolio loaded: {hero.portfolio.name_pt}')
    else:
        print('Portfolio is None (deleted or missing)')
else:
    print('No hero images with portfolio_id found')
db.close()
"
```

Expected: If portfolio is deleted, frontend should handle gracefully (no name displayed)

- [ ] **Step 6: Final verification commit**

```bash
git add -A
git commit -m "test: verify hero project names feature complete" --allow-empty
```

---

## Testing Checklist

After completing all tasks, verify:

- [ ] Hero images can be added from project images
- [ ] Added hero images have portfolio_id set
- [ ] Project name displays at top-center of home page
- [ ] Project name fades smoothly when slideshow advances
- [ ] Project name displays in correct language (PT/EN)
- [ ] Legacy hero images without project work gracefully
- [ ] Standalone hero upload form is removed from admin
- [ ] No errors in browser console
- [ ] No errors in server logs

## Rollback Plan

If issues occur:

1. Revert commits in reverse order:
   ```bash
   git log --oneline -6  # Find commits
   git revert <commit-hash>  # Revert specific commit
   ```

2. Remove portfolio_id column if needed:
   ```bash
   python -c "
   from app.db.session import engine
   from sqlalchemy import text
   with engine.connect() as conn:
       conn.execute(text('ALTER TABLE hero_images DROP COLUMN portfolio_id'))
       conn.commit()
   "
   ```

3. Restore the upload form section in `app/templates/admin/settings.html` from git history
