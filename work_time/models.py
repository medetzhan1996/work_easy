from calendar import monthrange, monthcalendar
from datetime import datetime
from typing import List, Dict

from django.conf import settings
from django.db import models
from collections import defaultdict

from account.models import User


class WorkTimeManager(models.Manager):

    def get_weekend_work_times_for_users(self, users: List[User]) -> Dict[int, Dict[int, bool]]:
        work_times = self.filter(user__in=users)
        user_work_times = defaultdict(lambda: defaultdict(bool))
        for work_time in work_times:
            user_work_times[work_time.user_id][work_time.week] = work_time.status
        return user_work_times

    def _is_working_day(self, day: int, day_week: int, weekends: Dict[int, bool]) -> bool:
        return day != 0 and weekends.get(day_week, False) == WorkTime.WORKING

    def get_working_days_for_users(self, users: List[User], year: int, month: int) -> Dict[int, int]:
        weekend_work_times = self.get_weekend_work_times_for_users(users)
        calendar_month = monthcalendar(year, month)
        user_working_days = defaultdict(int)
        for user in users:
            weekends = weekend_work_times.get(user.id, {})
            user_working_days[user.id] = sum(
                self._is_working_day(day, day_week, weekends)
                for week in calendar_month
                for day_week, day in enumerate(week)
            )

        return user_working_days


class WorkTime(models.Model):
    WEEK_CHOICES = (
        (0, "Пн"),
        (1, "Втр"),
        (2, "Срд"),
        (3, "Чтв"),
        (4, "Птн"),
        (5, "Суб"),
        (6, "Воск")
    )

    week = models.PositiveSmallIntegerField(choices=WEEK_CHOICES, default=0)
    WORKING = 'working'
    DAY_OFF = 'non-working'

    STATUS_CHOICES = (
        (WORKING, 'Рабочий день'),
        (DAY_OFF, 'Выходной'),
    )

    status = models.CharField(
        max_length=80,
        choices=STATUS_CHOICES,
        default=WORKING,
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    objects = WorkTimeManager()


class AttendanceManager(models.Manager):

    def calculate_salary_for_month(self, users: List[User], monthly_salary: float,
                                   working_days_for_users: Dict[int, int], year: int, month: int) -> Dict[int, float]:
        user_attendances = self.get_attendance_for_users(users, year, month)
        salaries = {}

        for user in users:
            working_days = working_days_for_users.get(user.id, 0)
            if working_days == 0:
                continue

            daily_salary = monthly_salary / working_days
            attendance_working_days = self._get_working_days_for_user(user_attendances[user.id])
            salaries[user.id] = int(round(daily_salary * attendance_working_days, 0))
        return salaries

    def get_attendance_for_users(self, users: List[User], year: int, month: int) -> Dict[int, Dict[datetime.date, str]]:
        attendances = self.filter(
            date__year=year,
            date__month=month,
            user__in=users,
        )

        user_attendances = defaultdict(dict)
        for attendance in attendances:
            user_attendances[attendance.user.id][attendance.date] = attendance.status

        return user_attendances

    def _get_working_days_for_user(self, attendances: Dict[datetime.date, str]) -> int:
        return sum(1 for status in attendances.values() if status == Attendance.WORKING)


class Attendance(models.Model):
    WORKING = 'working'
    DAY_OFF = 'day_off'
    HOLIDAY = 'holiday'
    ABSENT = 'absent'

    STATUS_CHOICES = (
        (WORKING, 'Работает'),
        (DAY_OFF, 'Выходной'),
        (HOLIDAY, 'Праздничный'),
        (ABSENT, 'Прогул'),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=WORKING,
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    objects = AttendanceManager()
