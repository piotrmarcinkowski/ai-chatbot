from datetime import datetime, timezone

def get_current_timestamp() -> int:
    """Returns the current UTC timestamp in seconds."""
    return int(datetime.now(timezone.utc).timestamp())

def get_current_time() -> str:
    """Returns the current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()