from work_time.models import WorkTime, Attendance


class WorkTimeMixin:

    def get_user_work_times(self, users):
        return WorkTime.objects.get_weekend_work_times_for_users(users)

    def get_working_days_for_users(self, users, year, month):
        return WorkTime.objects.get_working_days_for_users(users, year, month)


class AttendanceMixin:

    def get_user_attendances(self, users, year, month):
        return Attendance.objects.get_attendance_for_users(users, year, month)

    def calculate_salary_for_month(self, users, salary, working_days_for_users, year, month):
        attendance_for_users = Attendance.objects.calculate_salary_for_month(
            users, salary, working_days_for_users, year, month)
        return attendance_for_users