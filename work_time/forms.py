from datetime import datetime, timedelta, date
from django import forms
from .models import Attendance, WorkTime


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ['date', 'user', 'status']

class WorkTimeForm(forms.ModelForm):

    class Meta:
        model = WorkTime
        fields = ['user', 'status', 'week']