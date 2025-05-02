from django.contrib import admin
from .models import Department, CustomUser

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'department', 'phone')
    list_filter = ('role', 'department')
    search_fields = ('username', 'email', 'phone')

admin.site.register(Department, DepartmentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)