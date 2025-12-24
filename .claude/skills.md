# HateWatch Skills

## /scrape
Run the Telegram scraper to fetch new messages from monitored channels.

```bash
cd /Users/imranmohammed/hatewatch && source venv/bin/activate && python scripts/run_scraper.py --limit 100
```

Report how many messages were scraped from each channel.

## /process
Run the Perspective API processor to score unprocessed messages for toxicity.

```bash
cd /Users/imranmohammed/hatewatch && source venv/bin/activate && python scripts/run_processor.py
```

Report how many messages were processed.

## /detect
Run spike detection to find unusual increases in hate speech.

```bash
cd /Users/imranmohammed/hatewatch && source venv/bin/activate && python scripts/run_spike_detector.py
```

Report any new spikes detected.

## /status
Check the current system status - API health, post counts, active alerts.

```bash
curl -s http://localhost:8000/api/stats
curl -s http://localhost:8000/api/countries
curl -s "http://localhost:8000/api/alerts?active_only=true"
```

Present a summary of:
- Total posts in last 24h
- Average toxicity
- Number of active alerts
- Countries being monitored
- List any critical or high severity alerts

## /add-channel <username> <country>
Add a new Telegram channel to monitor. Read the current channels.json, add the new channel, and save.

Arguments:
- username: Telegram channel username (without @)
- country: Country name for the channel

After adding, run the scraper to fetch initial messages.

## /report
Generate a summary report of hate speech activity.

Query the API for:
- Stats from /api/stats
- Active alerts from /api/alerts
- Timeline from /api/timeline

Create a markdown report with:
- Executive summary
- Key metrics
- Active alerts with severity
- Toxicity trends
- Recommendations

## /export <alert_id>
Export evidence for a specific alert as CSV.

```bash
curl -O "http://localhost:8000/api/export/{alert_id}"
```

## /start-monitoring
Start continuous monitoring (scraper + processor).

Explain that the user needs to run these in separate terminal windows:
```bash
# Terminal 1 - Scraper
cd /Users/imranmohammed/hatewatch && source venv/bin/activate && python scripts/run_scraper.py --continuous

# Terminal 2 - Processor
cd /Users/imranmohammed/hatewatch && source venv/bin/activate && python scripts/run_processor.py --continuous
```

## /dashboard
Open the dashboard in the browser and check if servers are running.

```bash
open http://localhost:4000
curl -s http://localhost:8000/health
```

If API is not running, start it:
```bash
cd /Users/imranmohammed/hatewatch && source venv/bin/activate && uvicorn api.main:app --reload --port 8000
```
