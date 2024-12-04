from datetime import datetime, timedelta, time
import pytz

#maybe need a better name?
NUM_MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

def convert_to_local_time(utc_dt: datetime) -> datetime:
    local_tz = pytz.timezone("Asia/Jakarta")
    local_dt = utc_dt.astimezone(local_tz)
    return local_dt


def get_end_of_date(utc_dt: datetime) -> datetime:
    local_tz = pytz.timezone("Asia/Jakarta")
    local_dt = utc_dt.astimezone(local_tz)
    last_time_today = datetime.combine(local_dt, time(23, 59, 59, 999999))
    return local_tz.localize(last_time_today)

def convert_number_to_month(month_number: int) -> str:
    
    return NUM_MONTHS[month_number]


def is_date_string_format(date_string: str, format: str) -> bool:
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False
    

def get_month_difference(first_month: str, second_month: str, date_format: str = "%Y-%m") -> int:
    try:
        first_date = datetime.strptime(first_month, date_format)
        second_date = datetime.strptime(second_month, date_format)
    except ValueError as e:
        raise ValueError(
            f"Invalid date or format. Ensure the dates match the provided format '{date_format}'."
        ) from e
    

    return (second_date.year - first_date.year) * 12 + (second_date.month - first_date.month)


    

