# HateWatch

Hate speech intelligence platform that monitors Telegram channels, detects spikes in toxicity, and delivers actionable intelligence.

## Quick Start

### 1. Setup

```bash
cd hatewatch
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure API Keys

Edit `.env` with your credentials:

- **Telegram API**: Get from https://my.telegram.org
- **Perspective API**: Get from Google Cloud Console

### 3. Add Channels to Monitor

Edit `scraper/channels.json`:

```json
{
  "channels": [
    {
      "username": "your_channel_username",
      "country": "Country",
      "language": "en",
      "category": "political"
    }
  ]
}
```

### 4. Initialize Database

```bash
python -c "import asyncio; from database.connection import init_db; asyncio.run(init_db())"
```

### 5. Run Components

```bash
# Terminal 1: Scraper
python scripts/run_scraper.py --continuous

# Terminal 2: Processor
python scripts/run_processor.py --continuous

# Terminal 3: API Server
uvicorn api.main:app --reload --port 8000

# Terminal 4: Dashboard
cd dashboard
npm install
npm start
```

## Architecture

```
Telegram Scraper → Processing (Perspective API) → PostgreSQL/SQLite
                                                        ↓
                                                   FastAPI → React Dashboard
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stats` | Summary statistics |
| `GET /api/alerts` | Active spike alerts |
| `GET /api/alerts/{id}` | Alert details with posts |
| `GET /api/timeline` | Toxicity over time |
| `GET /api/posts` | Browse posts |
| `GET /api/export/{id}` | Export alert as CSV |

## Scripts

| Script | Purpose |
|--------|---------|
| `run_scraper.py` | Fetch messages from Telegram |
| `run_processor.py` | Score posts with Perspective API |
| `run_spike_detector.py` | Detect toxicity spikes |
| `seed_channels.py` | Add channels from JSON |
| `backfill.py` | Fetch historical data |

## Security

- Never commit `.env` or `.session` files
- Keep Telegram session file secure
- Consider IP restrictions on database
