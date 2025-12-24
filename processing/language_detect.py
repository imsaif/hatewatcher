import logging
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

DetectorFactory.seed = 0


def detect_language(text: str) -> str | None:
    if not text or len(text.strip()) < 10:
        return None

    try:
        return detect(text)
    except LangDetectException:
        return None
    except Exception as e:
        logger.warning(f"Language detection error: {e}")
        return None
