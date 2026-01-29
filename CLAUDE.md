# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend
```bash
python app.py  # Start Flask dev server at http://0.0.0.0:8000
```

### Docker
```bash
docker build -t utility-bills-tracker .
docker run -p 8000:8000 -v /data:/data utility-bills-tracker
```

## Architecture

This is a utility bills tracker web application with server-side rendered Jinja2 templates and Flask backend.

### Tech Stack
- **Backend:** Python 3.12, Flask, SQLite (raw SQL, no ORM)
- **Templates:** Jinja2 (Flask's built-in templating)
- **Frontend Interactivity:** HTMX 1.9.10 (loaded from CDN)
- **Styling:** Pico CSS v2 (loaded from CDN)
- **Production:** Gunicorn, Docker single-stage build

### Data Flow
1. Flask renders Jinja2 templates with data from SQLite
2. Forms submit to Flask routes for processing
3. HTMX handles dynamic interactions (e.g., delete without page reload)

### Routes
```
# Template Routes
GET    /                    - Bills list page
GET    /add                 - Create bill form
GET    /edit/<id>           - Edit bill form
GET    /history             - Usage history page with charts

# Form Submission Routes
POST   /bills/create        - Handle create form submission
POST   /bills/update/<id>   - Handle update form submission

# API Endpoints (used by HTMX)
DELETE /api/bills/<id>      - Delete bill (returns empty response for HTMX)

# Health Check
GET    /health              - Health check
```

### Templates
- `templates/base.html` - Base layout with HTML boilerplate, Pico CSS, HTMX script
- `templates/bills_list.html` - Bills list table with HTMX delete functionality
- `templates/bill_form.html` - Create/edit form (handles both modes)

### Database
SQLite with a single `bills` table containing cost fields (gas, electricity delivery/generation, other), usage fields (gas therms, electricity kWh by rate tier), and metadata (date which is unique, timestamps).

### Environment Variables
- `DATABASE_PATH` - SQLite database file location (default: `bills.db`)
- `FLASK_ENV` - Set to `production` in Docker
