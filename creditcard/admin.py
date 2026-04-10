from django.contrib import admin
from .models import CreditCardApplication

@admin.register(CreditCardApplication)
class CreditCardApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_name', 'card_type', 'status', 'salary', 'created_at']
    list_filter = ['status', 'card_type', 'created_at']
    search_fields = ['applicant_name', 'applicant_email', 'applicant_phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Applicant Info', {'fields': ('applicant_name', 'applicant_email', 'applicant_phone')}),
        ('Financial Info', {'fields': ('salary', 'currency')}),
        ('Application Details', {'fields': ('card_type', 'status', 'processed_by', 'remarks')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
