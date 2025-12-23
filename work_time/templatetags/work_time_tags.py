from django import template

register = template.Library()


@register.filter
def day_of_week(date):
    days = {
        "Monday": "пн",
        "Tuesday": "вт",
        "Wednesday": "ср",
        "Thursday": "чт",
        "Friday": "пт",
        "Saturday": "сб",
        "Sunday": "вс",
    }
    return days[date.strftime("%A")]


@register.simple_tag
def get_week_working(user_work_times, user_id, weekday):
    return user_work_times.get(user_id, {}).get(weekday, '')


@register.simple_tag
def get_attendance_status(user_attendances, user_id, date):
    return user_attendances.get(user_id, {}).get(date, '')

@register.simple_tag
def get_week_working_status(user_work_times, user_id, weekday):
    return user_attendances.get(user_id, {}).get(weekday, '')