from django.urls import path
from .views import *

urlpatterns = [
    path('user_passbook/<str:user_id>', UserPassbook.as_view()),
    path('user_balances/<str:user_id>', UserBalances.as_view()),
    path('add_expense', AddExpense.as_view())
]