from django.urls import path
from . import views
app_name = 'work_time'

urlpatterns = [
    path('attendance/', views.AttendanceView.as_view(), name="attendance"),
    path('week/work_time/', views.WeekWorkTime.as_view(), name="week_work_time"),
    path('attendance/form/', views.AttendanceFormView.as_view(), name="attendance_form"),
    path('week/work_time/form/', views.WorkTimeFormView.as_view(), name="work_time_form"),
]
