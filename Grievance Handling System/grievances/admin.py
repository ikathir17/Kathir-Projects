# grievances/admin.py
from django.contrib import admin
from .models import Grievance, GrievanceLog, GrievanceUpdate, Attachment, Feedback

@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'issue_type', 'status', 'created_at')
    list_filter = ('status', 'issue_type', 'department')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'grievance_id', 'customer_name', 'department_name', 'assigned_employee_name', 'rating', 'created_at')
    list_filter = ('rating', 'department', 'created_at')
    search_fields = ('grievance__id', 'customer__username', 'customer__email', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def customer_name(self, obj):
        return f"{obj.customer.get_full_name() or obj.customer.username}"
    customer_name.short_description = 'Customer'
    
    def department_name(self, obj):
        return obj.department.name
    department_name.short_description = 'Department'
    
    def assigned_employee_name(self, obj):
        return f"{obj.assigned_employee.get_full_name() or obj.assigned_employee.username}"
    assigned_employee_name.short_description = 'Assigned Employee'
    
    def grievance_id(self, obj):
        return f"#{obj.grievance.id}"
    grievance_id.short_description = 'Grievance ID'

    fieldsets = (
        ('Feedback Information', {
            'fields': ('grievance', 'rating', 'comment')
        }),
        ('Assignment Details', {
            'fields': ('customer', 'department', 'assigned_employee')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )