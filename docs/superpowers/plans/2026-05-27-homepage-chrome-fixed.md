# Homepage Chrome Fixed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the homepage logo, top navigation, language switcher, bottom about link, and copyright pinned to the viewport during scroll.

**Architecture:** Add a homepage-specific body class in the shared base template, then apply homepage-only fixed-position rules for the shared chrome so other pages keep their current layout behavior.

**Tech Stack:** FastAPI, Jinja2 templates, global CSS, Playwright CLI for verification

---

### Task 1: Add homepage-specific styling hook

**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/templates/index.html`

- [ ] Add a `body_class` template block to `base.html`
- [ ] Set `body_class` to `home-page` in `index.html`

### Task 2: Force homepage chrome to use fixed positioning

**Files:**
- Modify: `app/static/css/style.css`

- [ ] Add homepage-only fixed-position rules for `.logo-center`, `.top-nav-global`, `footer`, and `.bottom-nav`
- [ ] Preserve existing offsets so the visual layout stays unchanged

### Task 3: Verify the fix

**Files:**
- Modify: none

- [ ] Run `git diff --check -- app/templates/base.html app/templates/index.html app/static/css/style.css`
- [ ] Run a Playwright check against `http://127.0.0.1:8000/` and confirm the homepage chrome elements report `position: fixed`
