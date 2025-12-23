from utils import get_start_end_date_by_month
from .models import Salary, Penalty
from accounting.models import Transaction
from work_time.models import WorkTime, Attendance


class SalaryService:

    @staticmethod
    def get_salary_data(users, year, month):
        start_date, end_date = get_start_end_date_by_month(year, month)
        income_for_employees = Transaction.objects.get_income_for_employees(users, start_date, end_date)
        working_days_for_users = WorkTime.objects.get_working_days_for_users(users, year, month)
        calculated_salaries = Attendance.objects.calculate_salary_for_month(
            users, 120000, working_days_for_users, year, month)
        salaries = Salary.objects.get_salaries_for_month(users, year, month)
        penalties = Penalty.objects.get_total_penalty_by_users(users, year, month)
        return {
            'income_for_employees': income_for_employees,
            'calculated_salaries': calculated_salaries,
            'salaries': salaries,
            'penalties': penalties,
            'salary_advances': {}
        }
