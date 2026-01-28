# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend (run from `frontend/` directory)
```bash
npm run dev       # Start Vite dev server at http://0.0.0.0:3000
npm run build     # Build for production (outputs to dist/)
npm run lint      # Run ESLint
npm run preview   # Preview production build
```

### Backend
```bash
python backend/app.py  # Start Flask dev server at http://0.0.0.0:5000
```

### Docker
```bash
docker build -t utility-bills-tracker .
docker run -p 5000:5000 -v /data:/data utility-bills-tracker
```

## Architecture

This is a utility bills tracker web application with a React SPA frontend and Flask REST API backend.

### Tech Stack
- **Frontend:** React 19, React Router 7, Vite, vanilla CSS
- **Backend:** Python 3.12, Flask, SQLite (raw SQL, no ORM)
- **Production:** Gunicorn, Docker multi-stage build

### Data Flow
1. Frontend dev server proxies `/api/*` requests to backend (configured in `vite.config.js`)
2. Backend serves REST API at `/api/bills` endpoints
3. In production, Flask serves the built SPA static files and handles SPA routing fallback

### API Endpoints
```
GET    /api/bills           - List all bills (ordered by date DESC)
GET    /api/bills/<id>      - Get single bill
POST   /api/bills           - Create bill (date required, others optional)
PUT    /api/bills/<id>      - Update bill
DELETE /api/bills/<id>      - Delete bill
GET    /api/health          - Health check
```

### Frontend Routes
- `/` - Bills list view (BillsList component)
- `/add` - New bill form
- `/edit/:id` - Edit existing bill

### Database
SQLite with a single `bills` table containing cost fields (gas, electricity delivery/generation, other), usage fields (gas therms, electricity kWh by rate tier), and metadata (date which is unique, timestamps).

### Environment Variables
- `DATABASE_PATH` - SQLite database file location (default: `bills.db`)
- `FLASK_ENV` - Set to `production` in Docker
