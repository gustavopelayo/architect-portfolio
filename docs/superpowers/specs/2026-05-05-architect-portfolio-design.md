# Architect Portfolio Website Design Specification

## Project Overview
Create a portfolio website for an architect to showcase their work with a backoffice CMS for managing portfolio items. The site will focus on displaying architectural projects with images, descriptions, and technical details, inspired by the clean, minimalist aesthetic of andre tavares.net.

## Style Inspiration
Based on andre tavares.net, the design should feature:
- Minimalist, clean layout with generous white space
- Strong typographic hierarchy
- Grid-based layout for project showcases
- Subtle hover effects and transitions
- Focus on high-quality imagery
- Simple navigation structure
- Monochromatic color scheme with accent colors for emphasis

## Core Requirements
- Frontend: TypeScript (though we're using a monolithic FastAPI approach with Jinja2 templates)
- Backend: FastAPI with Python
- Database: MySQL
- Features:
  - Public portfolio showcase
  - Backoffice CMS for managing portfolio items
  - Portfolio items include: name, description, photos, technical photos, year, location/address
  - Ability to add, edit, delete portfolio items through the backoffice

## Architecture Decision
We've chosen Approach 1: Monolithic FastAPI + Jinja2 Templates
- Single codebase with FastAPI backend serving both API and frontend templates
- Simpler to deploy and maintain
- Good for portfolio sites with moderate traffic

## System Components

### 1. Backend (FastAPI)
- RESTful API endpoints for portfolio management
- Jinja2 template rendering for server-side pages
- MySQL database integration using SQLAlchemy ORM
- Authentication system for backoffice access
- File upload handling for project images

### 2. Frontend (Jinja2 Templates)
- Server-rendered HTML pages with minimal JavaScript for interactivity
- Responsive design using CSS inspired by andre tavares.net (minimalist, clean aesthetic)
- Template inheritance for consistent layout
- Public routes: home, portfolio gallery, project detail, about, contact
- Private routes: dashboard, portfolio management (CRUD operations)
- Design focuses on: generous white space, strong typography, grid layouts, high-quality imagery focus

### 3. Database (MySQL)
- Portfolio table with fields:
  - id (primary key)
  - name (string)
  - description (text)
  - year (integer)
  - location (string)
  - created_at (timestamp)
  - updated_at (timestamp)
- Portfolio_images table for regular project photos
- Technical_images table for technical drawings/details
- User table for backoffice authentication

## Data Flow
1. User visits public site -> FastAPI renders Jinja2 templates -> Database queried for portfolio items
2. User accesses backoffice -> Authentication check -> FastAPI serves admin templates
3. Admin submits form -> FastAPI processes -> Database updated -> File uploads stored
4. FastAPI serves updated content on subsequent requests

## Key Features

### Public-Facing Features
- Homepage with featured projects in a clean grid layout
- Portfolio gallery with filtering capabilities and minimalist presentation
- Individual project detail pages with image galleries focusing on high-quality visuals
- About page describing the architect's philosophy/experience with strong typography
- Contact form for inquiries with clean, simple design
- All pages featuring generous white space, grid-based layouts, and focus on imagery

### Backoffice Features
- Secure login system
- Dashboard showing portfolio statistics
- CRUD operations for portfolio items:
  - Create: Form with fields for all project data plus image uploads
  - Read: List view of all projects with search/filter
  - Update: Edit form pre-populated with existing data
  - Delete: Confirmation dialog before removal
- Image management: Upload, reorder, delete images
- Rich text editor for project descriptions

## Technical Considerations

### Security
- Authentication and authorization for backoffice access
- CSRF protection for forms
- Input validation and sanitization
- Secure file upload handling (validate file types, limit sizes)
- Password hashing for user accounts

### Performance
- Database indexing on commonly queried fields
- Image optimization (compression, appropriate sizing)
- Caching strategies for static assets
- Lazy loading for image galleries

### Deployment
- Containerization with Docker for easy deployment
- Environment-based configuration
- Database migration system
- Static file serving optimization

## Error Handling
- Custom error pages (404, 500)
- Form validation feedback
- Database error handling with user-friendly messages
- File upload validation and error reporting

## Testing Strategy
- Backend API unit tests
- Frontend template testing
- Integration tests for critical workflows
- Manual testing plan for CMS functionality

## Future Enhancements
- Project categorization/filtering system
- Client testimonials section
- Blog/news section for architectural insights
- Multi-language support
- Analytics integration
- SEO optimization features

## Success Criteria
- Architect can easily add/update portfolio items without technical assistance
- Website loads quickly and looks professional on all devices
- Portfolio items display correctly with all images and descriptions
- Backoffice interface is intuitive for someone with technical comfort
- Site is secure against common web vulnerabilities
- Visual design reflects the clean, minimalist aesthetic of andre tavares.net with focus on imagery and typography