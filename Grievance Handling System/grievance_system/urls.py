"""
URL configuration for grievance_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import register_view, login_view, logout_view, dashboard_view, register_admin_view
from grievances.views import (
    admin_dashboard, employee_dashboard, customer_dashboard, grievance_detail,
    get_employees_by_department, profile, grievance_logs, escalated_grievances, reviews,
    delete_grievance, admin_grievance_logs, submit_feedback
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('customer-dashboard/', customer_dashboard, name='customer_dashboard'),
    path('grievance/<int:pk>/', grievance_detail, name='grievance_detail'),
    path('', login_view, name='home'),
    path('api/employees/', get_employees_by_department, name='get_employees'),
    path('register-admin/', register_admin_view, name='register_admin'),
    path('grievance/<int:pk>/delete/', delete_grievance, name='delete_grievance'),
    path('grievance-logs/', grievance_logs, name='grievance_logs'),
    path('admin/grievance-logs/', admin_grievance_logs, name='admin_grievance_logs'),
    path('escalated-grievances/', escalated_grievances, name='escalated_grievances'),
    path('reviews/', reviews, name='reviews'),
    path('grievances/<int:grievance_id>/feedback/', submit_feedback, name='submit_feedback'),
    path('profile/', profile, name='profile'),
]
