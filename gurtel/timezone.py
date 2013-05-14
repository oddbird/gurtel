from datetime import datetime

import pytz


def now():
    """Return timezone-aware current datetime, in UTC."""
    return datetime.utcnow().replace(tzinfo=pytz.utc)
