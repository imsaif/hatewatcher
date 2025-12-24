from config import config


def calculate_severity(baseline: float, current: float) -> str:
    if baseline == 0 or baseline is None:
        return "unknown"

    increase = (current - baseline) / baseline

    if increase >= config.SEVERITY_CRITICAL:
        return "critical"
    elif increase >= config.SEVERITY_HIGH:
        return "high"
    elif increase >= config.SEVERITY_MEDIUM:
        return "medium"
    elif increase >= config.SEVERITY_LOW:
        return "low"
    else:
        return "normal"


def get_severity_order(severity: str) -> int:
    order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
        "normal": 0,
        "unknown": -1
    }
    return order.get(severity, -1)
