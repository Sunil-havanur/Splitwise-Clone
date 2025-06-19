from django.urls import path
from . import views
from .views import GroupCreateView, ExpenseCreateView, GroupBalanceView, UserBalanceView, create_group_view, add_expense,  group_balances_page, user_summary_page, dashboard

urlpatterns = [
    path('', views.api_overview),
    path('groups/', GroupCreateView.as_view(), name='create-group'),
    path('expenses/', ExpenseCreateView.as_view(), name='create-expense'),
    path('groups/<int:group_id>/balances/', GroupBalanceView.as_view(), name='group-balances'),
    path('users/<int:user_id>/balances/', UserBalanceView.as_view(), name='user-balances'),
    path('groups/create/', create_group_view, name='create-group'),
    path('expenses/add/', add_expense, name='add-expense'),
    path('groups/<int:group_id>/balances/page/', group_balances_page, name='group-balances-page'),
    path('users/<int:user_id>/summary/page/', user_summary_page, name='user-summary-page'),
    path('dashboard/', views.dashboard, name='dashboard'),

]

