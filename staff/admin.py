from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'employee_id', 'is_active_staff']
    list_filter = ['role', 'is_active_staff']
    search_fields = ['username', 'email', 'employee_id']
    fieldsets = (
        ('Personal Info', {'fields': ('username', 'email', 'first_name', 'last_name')}),
        ('Staff Info', {'fields': ('role', 'employee_id', 'department', 'is_active_staff')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
