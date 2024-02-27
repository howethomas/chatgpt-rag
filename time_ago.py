from datetime import datetime, timezone

def time_ago(time):
    """Convert a datetime object to a human-readable, relative string."""

    now = datetime.now(timezone.utc)
    diff = now - time
    
    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = diff.days
    weeks = days / 7
    months = days / 30
    years = days / 365
    
    if seconds < 60:
        return "just now"
    elif minutes < 60:
        return f"{int(minutes)} minutes ago"
    elif hours < 24:
        return f"{int(hours)} hours ago"
    elif days == 1:
        return "yesterday"
    elif days < 7:
        return f"{int(days)} days ago"
    elif weeks < 4:
        return f"{int(weeks)} weeks ago"
    elif months < 12:
        return f"{int(months)} months ago"
    else:
        return f"{int(years)} years ago"
