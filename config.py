import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")

    # Perspective API
    PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY", "")
    PERSPECTIVE_API_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./hatewatch.db")

    # App settings
    SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "5"))
    SPIKE_THRESHOLD = float(os.getenv("SPIKE_THRESHOLD", "1.5"))
    BASELINE_DAYS = int(os.getenv("BASELINE_DAYS", "7"))
    TOXICITY_THRESHOLD = float(os.getenv("TOXICITY_THRESHOLD", "0.7"))

    # Severity thresholds (percentage increase over baseline)
    SEVERITY_LOW = 0.5  # 50% increase
    SEVERITY_MEDIUM = 1.0  # 100% increase
    SEVERITY_HIGH = 2.0  # 200% increase
    SEVERITY_CRITICAL = 3.0  # 300% increase


config = Config()
