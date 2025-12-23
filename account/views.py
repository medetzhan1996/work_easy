from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from constants import MANAGER, MASTER, SUPERVISOR_PRODUCTION, ACCOUNTANT, GENERAL_MANAGER, DESIGNER, LOGISTIC

User = get_user_model()


class LoginView(LoginView):

    def get_success_url(self):
        if self.request.user.user_type == MANAGER or self.request.user.user_type == GENERAL_MANAGER:
            return reverse_lazy('orders:order_list')
        elif self.request.user.user_type == MASTER or self.request.user.user_type == SUPERVISOR_PRODUCTION or \
                self.request.user.user_type == DESIGNER:
            return reverse_lazy('orders:order_list')
        elif self.request.user.user_type == LOGISTIC:
            return reverse_lazy('orders:order_list')
        elif self.request.user.user_type == ACCOUNTANT:
            return reverse_lazy('accounting:transaction_list')
        else:
            return super().get_success_url()

