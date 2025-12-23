from account.models import User, Department
from content_type_constants import get_content_type_for_model, USER_CT_CACHE_KEY, DEPARTMENT_CT_CACHE_KEY
from sales_planning.models import SalesPlan


def get_sales_plan_for_objects(object_id, content_type, start_date, end_date):
    query = SalesPlan.objects.get_plan(object_id, content_type, start_date, end_date)
    return query


def create_or_update_sales_plan(data):
    sales_plan, created = SalesPlan.objects.update_or_create(
        content_type=data['content_type'],
        object_id=data['object_id'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        defaults={'target_sales': data['target_sales']}
    )
    return sales_plan, created


def annotate_sales_plans(data, start_date, end_date):
    user_ct = get_content_type_for_model(User, USER_CT_CACHE_KEY)
    department_ct = get_content_type_for_model(Department, DEPARTMENT_CT_CACHE_KEY)
    for department, users in data:
        department.sales_plan = get_sales_plan_for_objects(department.id, department_ct, start_date, end_date)
        for user in users:
            user.sales_plan = get_sales_plan_for_objects(user.id, user_ct, start_date, end_date)
