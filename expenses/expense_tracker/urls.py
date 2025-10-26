from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chart/', views.expense_chart, name='expense_chart'),
    path('add/', views.add_expense, name='add_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
