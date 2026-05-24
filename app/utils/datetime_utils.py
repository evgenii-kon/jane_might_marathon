from datetime import datetime, timezone

def utcnow_naive() -> datetime:
    """Возвращает текущее UTC время как offset-naive объект datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)