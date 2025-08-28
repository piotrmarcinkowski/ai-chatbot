from datetime import datetime, timezone

def get_current_timestamp() -> int:
    """Returns the current UTC timestamp in seconds."""
    return int(datetime.now(timezone.utc).timestamp())

def get_current_time() -> str:
    """Returns the current UTC time in ISO 8601 format."""
    return datetime.now(tz=timezone.utc).isoformat()
    
def get_current_local_time():
    """
    Returns the current local date and time. Use to get time in the current timezone.
    """
    # Get current local time (based on system timezone)
    return datetime.now().astimezone()

def get_local_time_zone():
    """
    Returns the current local timezone.
    """
    return datetime.now().astimezone().tzinfo