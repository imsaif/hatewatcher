# HateWatch - Project Memory

## Project Overview
HateWatch is a hate speech intelligence platform that monitors Telegram channels, scores messages for toxicity using Google's Perspective API, detects spikes in hate speech, and provides a dashboard for journalists and fact-checkers.

## Tech Stack
- **Backend:** Python 3.13, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React, Recharts
- **APIs:** Telegram (Telethon), Google Perspective API
- **Scraping:** Telethon for Telegram channels
- **Hosting:** Render (backend), Vercel (frontend)

## Key Files
- `scraper/telegram_scraper.py` - Fetches messages from Telegram channels
- `processing/perspective.py` - Scores toxicity via Perspective API
- `analysis/spike_detector.py` - Detects unusual toxicity increases
- `api/main.py` - FastAPI backend
- `dashboard/src/App.jsx` - React dashboard

## Live URLs
- **Dashboard:** https://dashboard-bay-tau.vercel.app
- **API:** https://hatewatch-api.onrender.com

## Commands
```bash
# Start API server
uvicorn api.main:app --reload --port 8000

# Start dashboard
cd dashboard && npm start

# Run scraper
python scripts/run_scraper.py --continuous

# Run processor
python scripts/run_processor.py --continuous
```

## Recent Sessions

### Session: 2026-01-30
- **Machine:** MacBook
- **Pattern:** DevOps / Deployment
- **Files changed:** 12
- **Notes:** Deployed HateWatch to production. Backend on Render (hatewatch-api.onrender.com), frontend on Vercel (dashboard-bay-tau.vercel.app). Added Dockerfile, nixpacks.toml, render.yaml, Procfile for deployment configs. Created /api/seed-demo endpoint for seeding demo data. Added "Last updated" timestamp to dashboard footer.

### Session: 2025-12-24
- **Machine:** MacBook
- **Pattern:** Full Stack Development
- **Files changed:** 46
- **Notes:** Built complete HateWatch MVP from spec - Telegram scraper, Perspective API integration, spike detection, FastAPI backend, React dashboard with country filtering. Added Claude Code skills for /scrape, /process, /detect, /status, /report commands.
