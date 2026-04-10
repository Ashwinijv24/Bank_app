from django.contrib import admin
from .models import Customer, Account, Transaction, Loan, CreditCard


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'aadhar_number', 'phone_number', 'created_at']
    search_fields = ['full_name', 'aadhar_number', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'customer', 'account_type', 'balance', 'status', 'created_at']
    list_filter = ['account_type', 'status', 'created_at']
    search_fields = ['account_number', 'customer__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_type', 'amount', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['account__account_number']
    readonly_fields = ['timestamp']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loan_amount', 'interest_rate', 'tenure_months', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ['card_number', 'customer', 'credit_limit', 'current_outstanding', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['card_number', 'customer__full_name']
    readonly_fields = ['created_at', 'updated_at']
