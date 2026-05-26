# Hero Images with Project Names - Design Specification

**Date**: 2026-05-26  
**Feature**: Display project names with hero slideshow images

## Overview

Extend the hero image slideshow on the main page to display the associated project name at the top-center of the page. When the slideshow cycles through images, the project name updates accordingly. This connects hero images to portfolio projects and provides context to visitors.

## Goals

- Display project name prominently at top-center of main page
- Update project name automatically as hero slideshow advances
- Simplify admin by requiring hero images to come from existing projects
- Maintain existing slideshow behavior (click to advance, 6-second intervals)

## Architecture

### Data Model Changes

**File**: `app/models/setting.py`

Modify the `HeroImage` model:
- Add `portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)`
- Add relationship: `portfolio = relationship("Portfolio", backref="hero_images")`
- Keep existing fields: `image_url`, `caption_pt`, `caption_en`, `sort_order`
- `portfolio_id` is nullable to maintain backward compatibility with existing standalone hero images

**Database Migration**:
- Add `portfolio_id` column to `hero_images` table
- Add foreign key constraint referencing `portfolios.id`
- No data migration required (existing NULL values are valid)

### Admin Interface

**File**: `app/templates/admin/settings.html`

**Changes**:
1. **Remove** the "ADD HERO IMAGE" section (file upload with caption fields)
2. **Keep** the "Hero Images" display section showing current hero images with Remove buttons
3. **Keep** the "FROM PROJECTS" grid section as the only way to add new hero images

**Backend**:
- Ensure the endpoint that adds images from projects (clicking "+" on project images) sets the `portfolio_id` field when creating the `HeroImage` record
- Remove or disable the standalone hero image upload endpoint
- Admin settings route must join `HeroImage` with `Portfolio` to display project information

### Frontend Display

**Files**: `app/templates/index.html`, `app/templates/base.html`, `app/static/css/style.css`

**HTML Structure**:
- Add a fixed project name display element positioned at top-center of the page
- Element appears above the hero slideshow
- Uses bilingual support: displays `name_pt` or `name_en` based on current language (`lang` variable)

**Data Attributes**:
- Each hero image (`<img class="hero-slide">`) needs a `data-project-id` attribute
- Also include `data-project-name-pt` and `data-project-name-en` attributes for quick access

**JavaScript Updates** (`index.html` inline script):
- On slide change (both click and auto-advance), read the project data attributes from the active slide
- Update the project name display element with the appropriate language
- Add smooth CSS transition (fade) when changing project names
- Handle edge case: if `data-project-id` is empty/missing, hide the project name element

**Styling**:
- Fixed positioning at top-center
- Use similar typography to the caption in reference screenshot ("COLETIVO 3º ESQUERDO")
- CSS transition for smooth fade effect (e.g., `transition: opacity 0.5s ease`)
- Ensure text is readable over varying image backgrounds (consider text shadow or subtle background)

**Backend Route** (`app/api/` or `app/main.py`):
- Index route must query `HeroImage` with eager loading of the `portfolio` relationship
- Pass portfolio data (id, name_pt, name_en) to the template for each hero image
- Use SQLAlchemy `joinedload` or similar to avoid N+1 queries

## Implementation Steps

### 1. Database Migration
- Create migration script to add `portfolio_id` column to `hero_images`
- Add foreign key constraint to `portfolios` table
- Test migration on development database

### 2. Update Models
- Modify `HeroImage` model in `app/models/setting.py`
- Add `portfolio_id` column and relationship
- Verify model with test queries

### 3. Backend Changes
- Update admin settings route to join portfolio data
- Verify/update endpoint for adding hero images from projects (must set `portfolio_id`)
- Remove or disable standalone hero image upload endpoint
- Update index route to eager-load portfolio data with hero images

### 4. Admin UI
- Remove "ADD HERO IMAGE" upload section from `app/templates/admin/settings.html`
- Test that clicking "+" on project images correctly creates hero images with `portfolio_id`

### 5. Frontend Display
- Add project name HTML element to `app/templates/base.html` or `app/templates/index.html`
- Add CSS styling for top-center fixed position and transitions
- Update hero slideshow JavaScript to handle project name display
- Add data attributes to hero image elements in template
- Test smooth transitions and language switching

### 6. Testing
- Test with hero images that have projects
- Test with legacy hero images without projects (should gracefully show nothing)
- Test language switching (PT/EN)
- Test single hero image (no cycling)
- Test empty hero images (fallback behavior)
- Test deleted project scenario

## Edge Cases

1. **Legacy hero images without `portfolio_id`**: 
   - Hide project name display when these images are active
   - No errors, graceful degradation

2. **Deleted projects**: 
   - If a project is deleted but hero image remains, the foreign key constraint should prevent this
   - Alternatively, set up cascading delete or null the `portfolio_id`
   - Frontend should handle NULL portfolio gracefully (hide name)

3. **Empty slideshow**: 
   - If no hero images exist, show default fallback image (current behavior)
   - No project name displayed

4. **Single hero image**: 
   - No cycling behavior
   - Project name stays static (no transitions needed)

5. **Missing translations**: 
   - If `name_pt` or `name_en` is NULL, fallback to the other language or hide display

## Files to Modify

- `app/models/setting.py` - Add portfolio_id to HeroImage model
- `app/templates/admin/settings.html` - Remove standalone upload section
- `app/templates/index.html` - Add project name display and update JavaScript
- `app/templates/base.html` - Possibly add project name element here if it should persist across pages
- `app/static/css/style.css` - Add styling for project name display
- Database migration script - Add portfolio_id column
- Admin API endpoint - Ensure portfolio_id is set when adding from projects
- Index route - Load portfolio data with hero images

## Future Enhancements

- Click on project name to navigate to project detail page
- Animate project name transitions (slide, scale, etc.)
- Show additional project metadata (year, location)
- Filter hero images by featured projects only
