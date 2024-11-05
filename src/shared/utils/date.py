from datetime import datetime, timedelta, time
import pytz


def convert_to_local_time(utc_dt: datetime) -> datetime:
    local_tz = pytz.timezone("Asia/Jakarta")
    local_dt = utc_dt.astimezone(local_tz)
    return local_dt


def get_end_of_date(utc_dt: datetime) -> datetime:
    local_tz = pytz.timezone("Asia/Jakarta")
    local_dt = utc_dt.astimezone(local_tz)
    last_time_today = datetime.combine(local_dt, time(23, 59, 59, 999999))
    return local_tz.localize(last_time_today)
