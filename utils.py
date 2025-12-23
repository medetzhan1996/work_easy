from calendar import monthrange
from datetime import timedelta, date, datetime

from django.contrib.contenttypes.models import ContentType


def month_dates(year, month):
    start_date = date(year, month, 1)
    while start_date.month == month:
        yield start_date
        start_date += timedelta(days=1)


def parse_year_month(year_month_str):
    try:
        year, month = map(int, year_month_str.split('-'))
        return year, month
    except ValueError:
        raise ValueError("Invalid year-month format!")


def get_current_year_month():
    now = datetime.now()
    return now.year, now.month


def format_year_month(year, month):
    return f"{year}-{month:02}"


def get_last_date(year, month):
    # Determine the number of days in the specified month
    last_day = monthrange(year, month)[1]

    # Create a datetime object for the last day of the specified month
    last_date = datetime(year, month, last_day)

    return last_date


def get_combine_content_type_data(data):
    return [
        {
            'id': f"{obj.id}_{ContentType.objects.get_for_model(obj).id}",
            'title': obj.title,
        }
        for obj in data
    ]


def get_start_end_date_by_month(year, month):
    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)
    return start_date, end_date


def string_to_date(date_string, date_format="%Y-%m-%d"):
    try:
        date_object = datetime.strptime(date_string, date_format)
        return date_object
    except ValueError:
        return None


def get_date_or_today(input_date):
    """Return the input date or today's date if the input is None."""
    if input_date is None:
        return date.today()
    return string_to_date(input_date)
