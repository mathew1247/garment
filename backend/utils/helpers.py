from datetime import datetime, timezone
import uuid

def get_current_timestamp():
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()

def generate_id(prefix="ID"):
    """
    Generate an ID with a specified prefix and short hex/timestamp.
    e.g. ORD-A1B2C3, NOT-123456
    """
    short_suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}{short_suffix}"

def is_valid_date(date_string):
    """Check if date string is in YYYY-MM-DD format."""
    if not isinstance(date_string, str):
        return False
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_past_date(date_string):
    """Check if date is strictly in the past (before today)."""
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()
        return dt < today
    except Exception:
        return False
