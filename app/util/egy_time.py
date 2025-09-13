
from datetime import datetime

import pytz


def get_egypt_time():
    """Get current time in Egypt timezone with DST handling"""
    egypt_tz = pytz.timezone('Africa/Cairo')
    utc_now = datetime.now(pytz.UTC)
    return utc_now.astimezone(egypt_tz)