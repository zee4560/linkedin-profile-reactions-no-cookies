from datetime import datetime, timedelta, timezone

def relative_token_from_days_ago(now_epoch: int, days_ago: int) -> str:
    """
    Produce a compact relative token like '5d' or '2w' given a days_ago integer.
    - 0..6 days -> 'Xd'
    - 7..29 days -> 'Xw'
    - 30+ days -> 'Xm' (approx months at 30 days)
    """
    if days_ago < 0:
        days_ago = 0
    if days_ago < 7:
        return f"{days_ago}d"
    if days_ago < 30:
        weeks = max(1, days_ago // 7)
        return f"{weeks}w"
    months = max(1, days_ago // 30)
    return f"{months}m"

def parse_relative_to_iso(relative_token: str) -> str:
    """
    Convert a compact token like '5d', '2w', '3m' into an ISO 8601 UTC timestamp in the past.
    """
    if not relative_token or len(relative_token) < 2:
        return datetime.now(timezone.utc).isoformat()

    num_part = "".join(ch for ch in relative_token if ch.isdigit())
    unit = relative_token[-1].lower()
    try:
        value = int(num_part)
    except ValueError:
        value = 0

    now = datetime.now(timezone.utc)
    if unit == "d":
        dt = now - timedelta(days=value)
    elif unit == "w":
        dt = now - timedelta(weeks=value)
    elif unit == "m":
        # Approximate a month as 30 days for this context
        dt = now - timedelta(days=30 * value)
    else:
        dt = now
    return dt.isoformat()