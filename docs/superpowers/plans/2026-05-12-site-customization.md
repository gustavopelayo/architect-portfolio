# Site Customization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add admin settings page for customizing taglines, logo, hero images, and contact info.

**Architecture:** Key-value `SiteSetting` model for text settings, separate `HeroImage` model for hero images. Settings loaded into template context via a helper function called in each route.

**Tech Stack:** FastAPI, SQLAlchemy, Jinja2

---

### Task 1: Create SiteSetting model

**Files:**
- Create: `app/models/setting.py`

- [ ] **Step 1: Write the model**

```python
from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class SiteSetting(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False, default="")
```

- [ ] **Step 2: Import model in init_db.py**

Add to `init_db.py`:
```python
from app.models.setting import SiteSetting
```

- [ ] **Step 3: Add HeroImage model import to init_db.py's imports**

Already imported via `from app.models.image import HeroImage` — but we need to add a `HeroImage` model.

Wait — the existing `image.py` has `PortfolioImage` and `TechnicalImage`. We need a separate `HeroImage` model. Let me add it to the setting model file or create a separate one.

Actually, let me keep it in `app/models/setting.py` alongside `SiteSetting` for simplicity since they're both related to site configuration.

--- wait, I'll reorganize:

**Files:**
- Create: `app/models/setting.py`

Contains both `SiteSetting` and `HeroImage` models.

- [ ] **Step 1: Write `app/models/setting.py`**

```python
from sqlalchemy import Column, Integer, String, Text
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
    caption = Column(String(255))
    sort_order = Column(Integer, default=0)
```

- [ ] **Step 2: Update `init_db.py` to import the new models**

```python
from app.models.setting import SiteSetting, HeroImage
```

- [ ] **Step 3: Commit**

```bash
git add app/models/setting.py init_db.py
git commit -m "feat: add SiteSetting and HeroImage models"
```

---

### Task 2: Create settings helper and template context injection

**Files:**
- Create: `app/core/settings_helper.py`
- Modify: `app/main.py`

- [ ] **Step 1: Write `app/core/settings_helper.py`**

```python
from app.db.session import SessionLocal
from app.models.setting import SiteSetting, HeroImage

def get_site_settings():
    db = SessionLocal()
    try:
        rows = db.query(SiteSetting).all()
        settings = {r.key: r.value for r in rows}
        hero_images = db.query(HeroImage).order_by(HeroImage.sort_order).all()
        settings["hero_images"] = hero_images
        return settings
    finally:
        db.close()
```

- [ ] **Step 2: Inject settings into templates in `app/main.py`**

Import at the top:
```python
from app.core.settings_helper import get_site_settings
```

Then add a helper that wraps TemplateResponse:

Actually, simpler: add settings to each route that renders a template. But that's repetitive. Better: create a dependency or just call the helper in each route.

Simplest approach — add to the routes that need it. But there are many routes. Let me add it to all template routes.

I'll create a small helper and call it at the top of each route that renders a template. Or better: since this is a small app, just add the settings context in each template route in main.py.

Let me take the approach of a single call in each route:

```python
settings = get_site_settings()
```

Then pass it to the template context.

For routes in `main.py` that need it: `home`, `portfolio_page`, `portfolio_detail`, `about`, `contact`, `admin_login`, `admin_dashboard`, `edit_project_form`, `create_project_form`.

Actually, I'll create a simpler approach. Let me modify each template route to include settings.

- [ ] **Step 3: Modify each template route in main.py**

Add to each route that uses `TemplateResponse`:
```python
from app.core.settings_helper import get_site_settings
# ...
settings = get_site_settings()
```

And pass to context:
```python
context={"request": request, ..., "settings": settings}
```

Affected routes: `home`, `portfolio_page`, `portfolio_detail`, `about`, `contact`, `admin_login`, `admin_dashboard`, `admin_login_post` (error case), `edit_project_form`, `create_project_form`.

- [ ] **Step 4: Commit**

```bash
git add app/core/settings_helper.py app/main.py
git commit -m "feat: add settings loader and inject into template context"
```

---

### Task 3: Create admin settings page

**Files:**
- Create: `app/templates/admin/settings.html`
- Modify: `app/main.py`
- Modify: `app/templates/admin/base_admin.html`
- Modify: `app/static/css/admin.css`

- [ ] **Step 1: Add settings routes to `main.py`**

```python
@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, db: Session = Depends(get_db)):
    from app.models.setting import SiteSetting, HeroImage
    settings_list = {r.key: r.value for r in db.query(SiteSetting).all()}
    hero_images = db.query(HeroImage).order_by(HeroImage.sort_order).all()
    site_settings = get_site_settings()
    return templates.TemplateResponse(
        request=request,
        name="admin/settings.html",
        context={
            "request": request,
            "settings_list": settings_list,
            "hero_images": hero_images,
            "settings": site_settings,
        }
    )

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
    upload_dir = Path("app/static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix or ".png"
    filename = f"logo{ext}"
    filepath = upload_dir / filename
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    row = db.query(SiteSetting).filter(SiteSetting.key == "logo_path").first()
    if row:
        row.value = f"/static/uploads/{filename}"
    else:
        db.add(SiteSetting(key="logo_path", value=f"/static/uploads/{filename}"))
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
    upload_dir = Path("app/static/uploads/hero")
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"hero_{int(datetime.now().timestamp())}{ext}"
    filepath = upload_dir / filename
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    max_order = db.query(db.func.max(HeroImage.sort_order)).scalar() or 0
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
```

Add import at top if not there:
```python
from app.core.settings_helper import get_site_settings
```

- [ ] **Step 2: Create `app/templates/admin/settings.html`**

```html
{% extends "admin/base_admin.html" %}

{% block title %}Site Settings - Admin{% endblock %}

{% block content %}
<section class="settings-page">
    <h1>Site Settings</h1>

    <section class="settings-section">
        <h2>Taglines</h2>
        <p class="settings-hint">One per line. They'll cycle on the front page.</p>
        <form action="/admin/settings/taglines" method="POST">
            <div class="form-group">
                <textarea name="taglines" rows="6">{{ settings_list.get('tagline', '') }}</textarea>
            </div>
            <button type="submit">Save Taglines</button>
        </form>
    </section>

    <hr class="section-divider">

    <section class="settings-section">
        <h2>Logo</h2>
        <p class="settings-hint">Current: {{ settings_list.get('logo_path', '/static/logo.png') }}</p>
        <form action="/admin/settings/logo" method="POST" enctype="multipart/form-data">
            <div class="form-group">
                <input type="file" name="file" accept="image/png,image/svg+xml,image/jpeg" required>
            </div>
            <button type="submit">Upload Logo</button>
        </form>
    </section>

    <hr class="section-divider">

    <section class="settings-section">
        <h2>Hero Images</h2>

        {% if hero_images %}
        <div class="current-media">
            {% for img in hero_images %}
            <div class="media-card">
                <img src="{{ img.image_url }}" alt="{{ img.caption or '' }}" style="height:120px">
                <div class="media-card-body">
                    <span class="caption">{{ img.caption or 'No caption' }}</span>
                    <a href="/admin/settings/hero/{{ img.id }}/delete" class="btn-delete-sm" onclick="return confirm('Delete this hero image?')">Remove</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="empty-state">No hero images yet.</p>
        {% endif %}

        <form action="/admin/settings/hero" method="POST" enctype="multipart/form-data" class="upload-form">
            <div class="form-group">
                <label for="hero_file">Add Hero Image</label>
                <input type="file" id="hero_file" name="file" required>
            </div>
            <div class="form-group">
                <label for="hero_caption">Caption (optional)</label>
                <input type="text" id="hero_caption" name="caption">
            </div>
            <button type="submit" class="btn-upload">Upload</button>
        </form>
    </section>

    <hr class="section-divider">

    <section class="settings-section">
        <h2>Contact Info</h2>
        <form action="/admin/settings/contact" method="POST">
            <div class="form-group">
                <label for="contact_email">Email</label>
                <input type="email" id="contact_email" name="email" value="{{ settings_list.get('contact_email', '') }}">
            </div>
            <div class="form-group">
                <label for="contact_phone">Phone</label>
                <input type="text" id="contact_phone" name="phone" value="{{ settings_list.get('contact_phone', '') }}">
            </div>
            <div class="form-group">
                <label for="contact_address">Address</label>
                <textarea id="contact_address" name="address" rows="3">{{ settings_list.get('contact_address', '') }}</textarea>
            </div>
            <div class="form-group">
                <label for="contact_blurb">Blurb</label>
                <textarea id="contact_blurb" name="blurb" rows="4">{{ settings_list.get('contact_blurb', '') }}</textarea>
            </div>
            <button type="submit">Save Contact Info</button>
        </form>
    </section>
</section>
{% endblock %}
```

- [ ] **Step 3: Add "Settings" nav link to `base_admin.html`**

```html
<a href="/admin/settings">Settings</a>
```

Add it before "View Site" or after "New Project".

- [ ] **Step 4: Add CSS for settings page to `admin.css`**

```css
/* Settings Page */
.settings-page h1 {
    font-family: "Playfair Display", serif;
    font-size: clamp(1.8rem, 4vw, 2.5rem);
    font-weight: 400;
    margin-bottom: 2rem;
}

.settings-section {
    margin-bottom: 2rem;
}

.settings-section h2 {
    font-family: "Playfair Display", serif;
    font-size: 1.25rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
}

.settings-hint {
    font-size: 0.8rem;
    color: var(--muted);
    margin-bottom: 1rem;
}
```

- [ ] **Step 5: Commit**

```bash
git add app/main.py app/templates/admin/settings.html app/templates/admin/base_admin.html app/static/css/admin.css
git commit -m "feat: add admin settings page for site customization"
```

---

### Task 4: Update front page to use dynamic settings

**Files:**
- Modify: `app/templates/index.html`
- Modify: `app/templates/base.html`
- Modify: `app/templates/portfolio.html`
- Modify: `app/templates/portfolio_detail.html`
- Modify: `app/templates/about.html`
- Modify: `app/templates/contact.html`

- [ ] **Step 1: Update `base.html` to use dynamic logo**

Replace:
```html
<img src="/static/logo.png" alt="" class="logo-icon">
```
With:
```html
<img src="{{ settings.get('logo_path', '/static/logo.png') }}" alt="" class="logo-icon">
```

- [ ] **Step 2: Update `index.html` for dynamic taglines and hero images**

```html
{% block content %}
<section class="hero">
    {% if settings.hero_images %}
    <div class="hero-slideshow">
        {% for img in settings.hero_images %}
        <img src="{{ img.image_url }}" alt="{{ img.caption or '' }}" class="hero-image hero-slide{% if loop.first %} active{% endif %}">
        {% endfor %}
    </div>
    {% else %}
    <img src="/static/uploads/hero-minimalist.jpg" alt="Architecture Studio" class="hero-image">
    {% endif %}
</section>

<section class="hero-content">
    {% set taglines = settings.get('tagline', 'Design is not only what we see, but what quietly transforms how we dwell.').split('\n') %}
    <h1 id="rotating-tagline">{{ taglines[0] }}</h1>
</section>

<script>
(function() {
    var taglines = {{ taglines | tojson | safe }};
    var idx = 0;
    var el = document.getElementById('rotating-tagline');
    if (taglines.length > 1) {
        setInterval(function() {
            idx = (idx + 1) % taglines.length;
            el.style.opacity = 0;
            setTimeout(function() {
                el.textContent = taglines[idx];
                el.style.opacity = 1;
            }, 300);
        }, 5000);
    }
})();
</script>
```

Wait, the taglines variable needs to be passed from the view. Let me adjust — the taglines come from `settings.tagline` split by newline. I'll do the splitting in the template:

```jinja
{% set tagline_list = settings.get('tagline', 'Design is not only what we see, but what quietly transforms how we dwell.').split('\n') %}
{% set tagline_json = tagline_list | tojson %}
```

And for hero images, add cycling JS:

```html
<script>
(function() {
    var taglines = {{ tagline_json | safe }};
    var idx = 0;
    var el = document.getElementById('rotating-tagline');
    if (taglines.length > 1 && el) {
        setInterval(function() {
            idx = (idx + 1) % taglines.length;
            el.style.opacity = 0;
            setTimeout(function() {
                el.textContent = taglines[idx];
                el.style.opacity = 1;
            }, 300);
        }, 5000);
    }

    var slides = document.querySelectorAll('.hero-slide');
    if (slides.length > 1) {
        var sidx = 0;
        setInterval(function() {
            slides[sidx].classList.remove('active');
            sidx = (sidx + 1) % slides.length;
            slides[sidx].classList.add('active');
        }, 6000);
    }
})();
</script>
```

Add CSS for slideshow:
```css
.hero-slideshow {
    position: relative;
}

.hero-slide {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: min(72vh, 760px);
    object-fit: cover;
    display: block;
    filter: grayscale(100%);
    opacity: 0;
    transition: opacity 1s ease, filter 0.3s ease;
}

.hero-slide.active {
    opacity: 1;
    position: relative;
}

.hero-slide:hover {
    filter: grayscale(0%);
}
```

And for the tagline:
```css
#rotating-tagline {
    transition: opacity 0.3s ease;
}
```

- [ ] **Step 3: Update `contact.html` to use dynamic settings**

Replace hardcoded contact info:
```html
<div class="contact-info">
    <p>{{ settings.get('contact_blurb', 'We would love to hear from you.') }}</p>
    <p>
        Email: {{ settings.get('contact_email', 'dadamoura@cloud.com') }}<br>
        Phone: {{ settings.get('contact_phone', '+351 931 110 004') }}<br>
        Address: {{ settings.get('contact_address', 'Rua Augusta, 123\nLisbon, Portugal') | replace('\n', '<br>') | safe }}
    </p>
</div>
```

- [ ] **Step 4: Commit**

```bash
git add app/templates/index.html app/templates/base.html app/templates/contact.html app/static/css/style.css
git commit -m "feat: update front page and contact page to use dynamic settings"
```

---

### Task 5: Update seed data with default settings

**Files:**
- Modify: `seed/seed_data.py`

- [ ] **Step 1: Add default settings and hero image creation to seed script**

Add after portfolio creation:
```python
from app.models.setting import SiteSetting, HeroImage

# Seed site settings
defaults = {
    "tagline": "Design is not only what we see, but what quietly transforms how we dwell.",
    "logo_path": "/static/logo.png",
    "contact_email": "dadamoura@cloud.com",
    "contact_phone": "+351 931 110 004",
    "contact_address": "Rua Augusta, 123\nLisbon, Portugal",
    "contact_blurb": "We would love to hear from you. Whether you have a project in mind or simply want to learn more about our studio, feel free to reach out.",
}

for key, value in defaults.items():
    existing = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if not existing:
        db.add(SiteSetting(key=key, value=value))
        print(f"  Created setting: {key}")

# Seed default hero image from seed images if available
import shutil
from pathlib import Path

hero_count = db.query(HeroImage).count()
if hero_count == 0:
    src = SEED_IMAGES / "09210756-c724-450f-a139-cd5823c875bb.jpg"
    if src.exists():
        dest = UPLOADS / "hero"
        dest.mkdir(parents=True, exist_ok=True)
        fname = f"hero_default{src.suffix}"
        shutil.copy2(src, dest / fname)
        db.add(HeroImage(
            image_url=f"/static/uploads/hero/{fname}",
            caption="",
            sort_order=0,
        ))
        print("  Created default hero image")

db.commit()
```

- [ ] **Step 2: Commit**

```bash
git add seed/seed_data.py
git commit -m "feat: seed default site settings and hero image"
```

---

### Task 6: Reset DB and verify

- [ ] **Step 1: Reset and reseed**

```bash
kill $(lsof -ti:8000) 2>/dev/null
rm -f test.db
.venv/bin/python init_db.py
.venv/bin/python seed/seed_data.py
```

- [ ] **Step 2: Restart server and check settings page**

```bash
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/app.log 2>&1 &
sleep 3
curl -s -c /tmp/cookies.txt -X POST http://localhost:8000/admin/login -d "username=admin&password=admin123" -o /dev/null
curl -s -b /tmp/cookies.txt http://localhost:8000/admin/settings | grep -o "Taglines\|Logo\|Hero\|Contact Info" | sort | uniq -c
```

- [ ] **Step 3: Verify front page renders**

```bash
curl -s http://localhost:8000 | grep -o "logo-icon\|rotating-tagline\|hero-slide" | sort | uniq -c
```

- [ ] **Step 4: Verify contact page renders dynamic info**

```bash
curl -s http://localhost:8000/contact | grep -o "dadamoura@cloud.com\|+351" | sort | uniq -c
```

- [ ] **Step 5: Commit final state**

```bash
git add -A && git commit -m "feat: complete site customization feature"
```
