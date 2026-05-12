# Site Customization

## Goal
Give the admin control over the front page (tagline, logo, hero images) AND the contact page (email, phone, address, blurb) — all from a new admin settings page.

## Data Model

### `SiteSetting` (table: `site_settings`)
| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| key | String(100), unique | e.g. `tagline`, `logo_path` |
| value | Text | |

Rows seeded by default:

| key | value |
|-----|-------|
| `tagline` | `Design is not only what we see, but what quietly transforms how we dwell.` |
| `logo_path` | `/static/logo.png` |
| `contact_email` | `dadamoura@cloud.com` |
| `contact_phone` | `+351 931 110 004` |
| `contact_address` | `Rua Augusta, 123\nLisbon, Portugal` |
| `contact_blurb` | `We would love to hear from you. Whether you have a project in mind or simply want to learn more about our studio, feel free to reach out.` |

### `HeroImage` (table: `hero_images`)
| Column | Type | Notes |
|--------|------|-------|
| id | Integer, PK | |
| image_url | String(255), not null | path to uploaded image |
| caption | String(255), nullable | |
| sort_order | Integer, default 0 | controls display order on front page |

## Admin UI

### New route: `/admin/settings`
Sections:
1. **Taglines** — textarea listing taglines, one per line. Saving updates the `tagline` setting (newline-separated).
2. **Logo** — file upload that saves to `app/static/uploads/logo/` and updates `logo_path` setting.
3. **Hero Images** — current list with delete buttons, upload form at the bottom. Images stored in `app/static/uploads/hero/`.
4. **Contact Info** — text inputs for email, phone, address (textarea), blurb (textarea).

### Routes
| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/settings` | Settings page |
| POST | `/admin/settings/taglines` | Update taglines |
| POST | `/admin/settings/logo` | Upload logo |
| POST | `/admin/settings/hero` | Upload hero image |
| GET | `/admin/settings/hero/{id}/delete` | Delete hero image |
| POST | `/admin/settings/contact` | Update contact info |

Nav link "Settings" added to admin header.

## Front Page Changes

### `templates/index.html`
- Tagline(s): read from setting, split by newline, cycle via JS fade transitions every ~5s
- Hero image(s): read all `HeroImage` rows ordered by `sort_order`, cycle via CSS/JS crossfade
- Logo: `base.html` reads `logo_path` from setting (fallback to `/static/logo.png`)

### `templates/contact.html`
- Email, phone, address, blurb all read from site settings (injected via template context)

### Context helper
A `get_settings()` helper loads all `SiteSetting` rows into a dict and injects them into every `TemplateResponse` via a dependency or middleware. Every template gets `settings.contact_email`, `settings.tagline`, etc.

## Seed Data
`seed/seed_data.py` updated to create default `SiteSetting` rows and a default `HeroImage` from `hero-minimalist.jpg`.

## Non-Goals
- No drag-to-reorder for hero images
- No rich text editing
- No per-page settings
