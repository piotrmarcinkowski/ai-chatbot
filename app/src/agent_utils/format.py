from datetime import datetime

def format_date(timestamp: int) -> str:
    """Formats a UTC timestamp (in seconds) to a human-readable string."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
           