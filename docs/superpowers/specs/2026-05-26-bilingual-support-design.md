# Bilingual Support Design (English/Portuguese)

**Date:** 2026-05-26  
**Status:** Approved  
**Languages:** English (en), Portuguese (pt)

## Overview

Add bilingual support to the Daniel Moura architecture portfolio website, allowing visitors to switch between English and Portuguese. All user-facing content will be translatable, with Portuguese as the default language and English as a secondary option.

## Goals

1. Allow visitors to choose their preferred language (EN/PT)
2. Persist language preference across visits via cookies
3. Enable admin to manage content in both languages side-by-side
4. Graceful fallback when translations are missing (Portuguese → English)
5. Maintain performance with minimal query overhead

## Non-Goals

- SEO-optimized language URLs (no `/en/` or `/pt/` paths)
- Automatic translation via APIs
- Support for additional languages beyond EN/PT
- Translation of admin panel interface (admin stays in current language)

## User Experience

### Language Switcher

**Location:** Header navigation, right side after "Contact" link

**Design:**
- Simple text links: `PT | EN`
- Current language is bold/highlighted
- Non-current language is clickable
- Minimal styling matching existing nav

**Behavior:**
- Click sets cookie and reloads page
- All content updates to selected language
- Preference persists for 365 days

### Language Detection Priority

1. User clicked language switcher → use selected language
2. Existing `lang` cookie → use stored preference
3. Browser `Accept-Language` header → auto-detect
4. Default to Portuguese

### Fallback Behavior

When content is missing in selected language:
- Try Portuguese version first (default)
- If Portuguese missing, try English
- If both missing, show empty string

## Architecture

### Approach: Database Column Duplication

Add `_pt` and `_en` suffixed columns to all content tables. This provides:
- Fast direct column access (no joins)
- Simple queries and templates
- Clear data model
- SQLite-friendly

**Alternative approaches considered:**
- Translation table pattern (rejected: too complex, slower queries)
- JSON field storage (rejected: limited SQLite JSON support, can't filter)

## Database Schema Changes

### Models to Update

#### Portfolio Model (`app/models/portfolio.py`)

**Add columns:**
- `name_pt` (String, 255, nullable)
- `name_en` (String, 255, nullable)
- `description_pt` (Text, nullable)
- `description_en` (Text, nullable)
- `location_pt` (String, 255, nullable)
- `location_en` (String, 255, nullable)

**Keep existing:** `name`, `description`, `location` (for backward compatibility)

#### SiteSetting Model (`app/models/setting.py`)

**New key-value pairs:**
- `site_name_pt`, `site_name_en`
- `copyright_pt`, `copyright_en`
- `tagline_pt`, `tagline_en`
- `contact_blurb_pt`, `contact_blurb_en`
- `about_title_pt`, `about_title_en`
- `about_body_pt`, `about_body_en`

**Non-translatable keys:** `logo_path`, `contact_email`, `contact_phone`, `contact_address`

#### HeroImage Model (`app/models/setting.py`)

**Add columns:**
- `caption_pt` (String, 255, nullable)
- `caption_en` (String, 255, nullable)

**Keep existing:** `caption` (for backward compatibility)

#### PortfolioImage & TechnicalImage Models (`app/models/image.py`)

**Add columns:**
- `caption_pt` (String, 255, nullable)
- `caption_en` (String, 255, nullable)

**Keep existing:** `caption` (for backward compatibility)

### Migration Strategy

**Phase 1: Add columns**
```sql
ALTER TABLE portfolio ADD COLUMN name_pt VARCHAR(255);
ALTER TABLE portfolio ADD COLUMN name_en VARCHAR(255);
ALTER TABLE portfolio ADD COLUMN description_pt TEXT;
ALTER TABLE portfolio ADD COLUMN description_en TEXT;
ALTER TABLE portfolio ADD COLUMN location_pt VARCHAR(255);
ALTER TABLE portfolio ADD COLUMN location_en VARCHAR(255);

ALTER TABLE hero_images ADD COLUMN caption_pt VARCHAR(255);
ALTER TABLE hero_images ADD COLUMN caption_en VARCHAR(255);

ALTER TABLE portfolio_images ADD COLUMN caption_pt VARCHAR(255);
ALTER TABLE portfolio_images ADD COLUMN caption_en VARCHAR(255);

-- (same pattern for technical_images)
```

**Phase 2: Copy existing data to Portuguese columns**
```sql
UPDATE portfolio SET 
  name_pt = name,
  description_pt = description,
  location_pt = location;

UPDATE hero_images SET caption_pt = caption;
UPDATE portfolio_images SET caption_pt = caption;
UPDATE technical_images SET caption_pt = caption;
```

**Phase 3: Create new SiteSetting key-value pairs**
- Copy current single values to `_pt` keys
- Leave `_en` keys for admin to fill

**Phase 4: Update seed data**
- Update `seed/seed_data.py` to include bilingual structure
- Ensures fresh installs have proper schema

## Static UI Text Translation

### Translation Files

**File:** `app/translations/en.json`
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
  }
}
```

**File:** `app/translations/pt.json`
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
  }
}
```

## Helper Functions

### File: `app/utils/i18n.py`

```python
def get_current_language(request: Request) -> str:
    """
    Determine current language from:
    1. Cookie 'lang'
    2. Accept-Language header
    3. Default to 'pt'
    
    Returns: 'pt' or 'en'
    """

def t(key: str, lang: str) -> str:
    """
    Get static translation from JSON files.
    
    Args:
        key: Dot-notation key (e.g., 'nav.about')
        lang: Language code ('pt' or 'en')
    
    Returns: Translated string
    
    Fallback: pt.json -> key itself
    """

def get_translated_field(obj, field_base: str, lang: str) -> str:
    """
    Get translated field from database object.
    
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

def load_translations(lang: str) -> dict:
    """
    Load translation JSON file.
    Cache in memory for performance.
    """
```

## Language Switching

### Cookie Specification

- **Name:** `lang`
- **Values:** `pt` | `en`
- **Expiry:** 365 days
- **Path:** `/`
- **SameSite:** Lax

### Routes

**Endpoint:** `GET /set-language`

**Query params:**
- `lang`: `pt` or `en`
- `redirect`: URL to return to (default: referrer or `/`)

**Behavior:**
1. Validate `lang` parameter
2. Set `lang` cookie
3. Redirect back to referring page

**Example:**
```
GET /set-language?lang=en&redirect=/portfolio
→ Sets cookie
→ Redirects to /portfolio
```

## Template Updates

### Base Template (`app/templates/base.html`)

**Add to navigation:**
```html
<ul class="nav-links">
    <li><a href="/">{{ t('nav.about') }}</a></li>
    <li><a href="/portfolio">{{ t('nav.portfolio') }}</a></li>
    <li><a href="/contact">{{ t('nav.contact') }}</a></li>
    <li class="lang-switcher">
        {% if current_lang == 'pt' %}
            <strong>PT</strong> | <a href="/set-language?lang=en">EN</a>
        {% else %}
            <a href="/set-language?lang=pt">PT</a> | <strong>EN</strong>
        {% endif %}
    </li>
</ul>
```

**CSS for language switcher:**
```css
.lang-switcher {
    margin-left: 1rem;
    font-size: 0.875rem;
}
.lang-switcher strong {
    font-weight: 600;
}
.lang-switcher a {
    opacity: 0.7;
}
```

### Public Templates

**Update all templates:**
- `index.html`
- `portfolio.html`
- `portfolio_detail.html`
- `about.html`
- `contact.html`

**Replace hardcoded text:**
```html
<!-- Before -->
<h1>Portfolio</h1>

<!-- After -->
<h1>{{ t('portfolio.heading') }}</h1>
```

**Replace database fields:**
```html
<!-- Before -->
<h2>{{ project.name }}</h2>

<!-- After -->
<h2>{{ get_translated_field(project, 'name', current_lang) }}</h2>
```

### FastAPI Integration

**Update main.py:**
```python
from app.utils.i18n import get_current_language, t, get_translated_field
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

# Register helpers as Jinja2 globals
templates.env.globals['t'] = t
templates.env.globals['get_translated_field'] = get_translated_field

# Add dependency to inject current_lang
async def get_lang_context(request: Request):
    return {"current_lang": get_current_language(request)}

# Use in route handlers
@app.get("/")
async def index(request: Request, lang_ctx: dict = Depends(get_lang_context)):
    return templates.TemplateResponse("index.html", {
        "request": request,
        **lang_ctx
    })
```

## Admin Panel Updates

### Admin Form Layout

**Structure:** Two-column side-by-side layout

```
┌──────────────────────────────────────────┐
│ Project Name                             │
├──────────────────┬───────────────────────┤
│ English          │ Português             │
│ [input]          │ [input]               │
└──────────────────┴───────────────────────┘

┌──────────────────────────────────────────┐
│ Description                              │
├──────────────────┬───────────────────────┤
│ English          │ Português             │
│ [textarea]       │ [textarea]            │
│                  │                       │
│                  │                       │
└──────────────────┴───────────────────────┘
```

### Forms to Update

#### Project Form (`admin/project_form.html`)

**Fields:**
- Name: `name_en` | `name_pt`
- Description: `description_en` | `description_pt`
- Location: `location_en` | `location_pt`
- Image captions: `caption_en` | `caption_pt`

#### Settings Form (`admin/settings.html`)

**Fields:**
- Site Name: `site_name_en` | `site_name_pt`
- Copyright: `copyright_en` | `copyright_pt`
- Tagline: `tagline_en` | `tagline_pt`
- Contact Blurb: `contact_blurb_en` | `contact_blurb_pt`
- About Title: `about_title_en` | `about_title_pt`
- About Body: `about_body_en` | `about_body_pt`

#### Hero Images

**Fields:**
- Caption: `caption_en` | `caption_pt`

### Admin CSS

**Add to `admin.css`:**
```css
.bilingual-field {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

.bilingual-field .lang-column {
    display: flex;
    flex-direction: column;
}

.bilingual-field label {
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
    opacity: 0.7;
}

@media (max-width: 768px) {
    .bilingual-field {
        grid-template-columns: 1fr;
    }
}
```

### Backend Route Updates

**Update POST handlers in `app/main.py`:**

```python
@app.post("/admin/projects/create")
async def create_project(
    name_en: str = Form(None),
    name_pt: str = Form(...),  # Portuguese required
    description_en: str = Form(None),
    description_pt: str = Form(...),
    location_en: str = Form(None),
    location_pt: str = Form(None),
    # ... other fields
):
    project = Project(
        name_pt=name_pt,
        name_en=name_en,
        description_pt=description_pt,
        description_en=description_en,
        location_pt=location_pt,
        location_en=location_en,
    )
    db.add(project)
    db.commit()
```

**Validation:**
- At least Portuguese must be filled (required fields)
- English can be optional/empty

## Deployment Strategy

### Phase 1: Backend + Database (Non-Breaking)

**Deploy:**
1. Add new `_pt` and `_en` columns to all models
2. Run database migration
3. Copy existing data to `_pt` columns
4. Deploy backend code with translation helpers

**Impact:** No user-facing changes yet, safe to deploy

### Phase 2: Admin Panel

**Deploy:**
1. Update admin templates with side-by-side fields
2. Update POST handlers to accept both languages
3. Admin can start filling English translations

**Impact:** Admin sees new UI, can add translations

### Phase 3: Frontend

**Deploy:**
1. Add language switcher to header
2. Update all public templates to use `t()` and `get_translated_field()`
3. Add translation JSON files

**Impact:** Users see language switcher, can switch languages

### Phase 4: Cleanup (Optional)

**After verification:**
1. Can remove old single-language columns
2. Or keep as backup for rollback

## Rollback Plan

**If issues arise:**
1. Hide language switcher via CSS (`display: none`)
2. Revert templates to use old single-language columns
3. Old data still intact, no data loss

**Database rollback:**
- All old columns remain until Phase 4
- Can switch back without data migration

## Testing Checklist

**Language Detection:**
- [ ] Cookie `lang=pt` shows Portuguese
- [ ] Cookie `lang=en` shows English
- [ ] No cookie + PT browser → shows Portuguese
- [ ] No cookie + EN browser → shows English
- [ ] Default (no hints) → shows Portuguese

**Language Switching:**
- [ ] Click PT → sets cookie, shows Portuguese
- [ ] Click EN → sets cookie, shows English
- [ ] Cookie persists across page loads
- [ ] Cookie persists after browser restart

**Content Fallback:**
- [ ] Portuguese content + no English → shows Portuguese
- [ ] English content + no Portuguese → shows English (fallback)
- [ ] Both missing → shows empty string
- [ ] Partial translation → shows available language

**Admin Panel:**
- [ ] Create project with both languages
- [ ] Create project with only Portuguese
- [ ] Edit existing project, add English
- [ ] Settings form saves both languages
- [ ] Image captions save both languages

**Public Pages:**
- [ ] Home page in both languages
- [ ] Portfolio list in both languages
- [ ] Portfolio detail in both languages
- [ ] About page in both languages
- [ ] Contact page in both languages
- [ ] Contact form labels in both languages

**Static UI:**
- [ ] Navigation labels translate
- [ ] Button text translates
- [ ] Form labels translate
- [ ] Success messages translate

## Files to Create

1. `app/utils/i18n.py` - Translation helpers
2. `app/translations/en.json` - English static text
3. `app/translations/pt.json` - Portuguese static text
4. `docs/superpowers/specs/2026-05-26-bilingual-support-design.md` - This spec

## Files to Modify

**Models:**
1. `app/models/portfolio.py` - Add `_pt`/`_en` columns
2. `app/models/setting.py` - Add `_pt`/`_en` columns to HeroImage
3. `app/models/image.py` - Add `_pt`/`_en` columns

**Templates:**
1. `app/templates/base.html` - Add language switcher, register helpers
2. `app/templates/index.html` - Use translation functions
3. `app/templates/portfolio.html` - Use translation functions
4. `app/templates/portfolio_detail.html` - Use translation functions
5. `app/templates/about.html` - Use translation functions
6. `app/templates/contact.html` - Use translation functions
7. `app/templates/admin/project_form.html` - Side-by-side fields
8. `app/templates/admin/settings.html` - Side-by-side fields

**Backend:**
1. `app/main.py` - Register Jinja2 helpers, update POST handlers, add `/set-language` route
2. `seed/seed_data.py` - Add bilingual seed data

**CSS:**
1. `app/static/css/style.css` - Language switcher styles
2. `app/static/css/admin.css` - Bilingual form layout

**Database:**
1. Create migration script or manual SQL for schema changes

## Success Criteria

1. Visitors can switch between EN/PT via header links
2. Language preference persists via cookie
3. All content displays in selected language
4. Missing translations fall back to Portuguese gracefully
5. Admin can edit both languages side-by-side
6. No performance degradation (direct column access)
7. Existing Portuguese content migrated without loss
8. Mobile responsive (side-by-side stacks vertically)

## Future Enhancements (Out of Scope)

- Additional languages beyond EN/PT
- SEO-optimized language URLs (`/en/`, `/pt/`)
- Automatic translation via APIs
- Admin panel language switching
- Per-user language preferences (if auth added)
- Translation management UI for static text
