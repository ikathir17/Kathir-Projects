from django.urls import path
from grievances.views import (
    home,
    dashboard,
    admin_dashboard,
    employee_dashboard,
    submit_grievance,
    grievance_detail,
    escalated_grievances,
    reviews,
    submit_feedback,
    profile_view
)

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('submit-grievance/', submit_grievance, name='submit_grievance'),
    path('grievance/<int:pk>/', grievance_detail, name='grievance_detail'),
    path('escalated-grievances/', escalated_grievances, name='escalated_grievances'),
    path('reviews/', reviews, name='reviews'),
    path('submit-feedback/<int:grievance_id>/', submit_feedback, name='submit_feedback'),
    path('profile/', profile_view, name='profile'),
] 