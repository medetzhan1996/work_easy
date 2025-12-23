import calendar
from datetime import date
from datetime import datetime, timedelta

from utils import parse_year_month, get_current_year_month


def get_base_date_or_today(base_date=None):
    """
    Возвращает дату, представленную параметром base_date, или текущую дату, если base_date не указан
    или не может быть преобразован в дату.

    :param base_date: Строка или объект date, представляющий базовую дату.
    :return: Объект date или текущая дата.
    """
    if base_date:
        if isinstance(base_date, str):
            try:
                return datetime.strptime(base_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        elif isinstance(base_date, date):
            return base_date
    return datetime.today().date()


def determine_period_dates(selected_period, base_date=None):
    base_date = get_base_date_or_today(base_date)

    if selected_period == 'year':
        start_date = datetime(base_date.year, 1, 1)
        end_date = datetime(base_date.year, 12, 31)
    elif selected_period == 'month':
        start_date = datetime(base_date.year, base_date.month, 1)
        if base_date.month == 12:
            end_date = datetime(base_date.year, 12, 31)
        else:
            end_date = datetime(base_date.year, base_date.month + 1, 1) - timedelta(days=1)
    elif selected_period == 'range':
        # Так как это утилитарная функция, мы будем передавать start_date и end_date напрямую.
        # Ваша логика для определения дат может отличаться.
        raise ValueError("For 'range' period, start_date and end_date should be explicitly provided.")
    else:
        raise ValueError("Invalid period type.")

    return start_date, end_date


def is_start_and_end_of_month(start, end):
    _, last_day_of_month = calendar.monthrange(start.year, start.month)
    return start.day == 1 and end.day == last_day_of_month and start.month == end.month


def is_start_and_end_of_year(start, end):
    return start.month == 1 and start.day == 1 and end.month == 12 and end.day == 31


def get_period_start_date(selected_period, value=None):
    if selected_period == 'month':
        year, month = parse_year_month(value) if value else get_current_year_month()
        date = f"{year}-{month}-01"
    elif selected_period == 'year':
        year, month = (value, None) if value else get_current_year_month()
        date = f"{year}-01-01"
    else:
        raise ValueError(f"Unsupported selected_period: {selected_period}")
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_selected_dates(period=None, period_val=None, start_date_str=None, end_date_str=None):
    selected_period = period if period else 'month'
    if selected_period == 'range':
        start_date = get_base_date_or_today(start_date_str)
        end_date = get_base_date_or_today(end_date_str)
    else:
        period_start_date = get_period_start_date(selected_period, period_val)
        start_date, end_date = determine_period_dates(selected_period, period_start_date)
    return selected_period, start_date, end_date

