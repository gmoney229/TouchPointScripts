#!python3

# Imports
import calendar
import datetime


# Functions
def my_now():
    # NOTE I think this is not really my time now but the computer's time?
    #       TODO pass in param for tz :)
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def utc_now():
    return datetime.datetime.now(datetime.UTC)


def get_first_day_of_month(year: int, month: int):
    return datetime.datetime.strptime('{0}-{1}-{2}'.format(year, month, 1), '%Y-%m-%d').date()


def get_last_day_of_month(year: int, month: int):
    # Create a date object for the first day of the next month
    next_month = datetime.date(year, month, 1) + datetime.timedelta(days=32)
    # Subtract one day to get the last day of the current month
    return next_month - datetime.timedelta(days=next_month.day)


def get_last_sunday():
    today = datetime.date.today()
    days_since_sunday = today.weekday() + 1  # Monday = 0, Sunday = 6
    last_sunday = today - datetime.timedelta(days=days_since_sunday)
    return last_sunday


def days_from_now(days: int, time_zone: datetime.timezone=None, now: datetime.datetime=None):
    """
    TODO come up with example case for time_zone and now being passed in...
            passing both time_zone and now is a little spaghetti :(
    ex.
        days_from_now(days=7, time_zone=datetime.UTC)
        days_from_now(days=7)
        days_from_now(days=7, now=datetime.datetime.now())
    """
    now = now if now is not None else datetime.datetime.now(time_zone)
    return now - datetime.timedelta(days)


def yesterday(**kwargs):
    return days_from_now(days=1, **kwargs)


def day_is(time_stamp, day_of_week: str):
    return calendar.day_name[time_stamp.weekday()].upper() == day_of_week.upper()
