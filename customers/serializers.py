from rest_framework import serializers
from .models import Customer, Account, Transaction, Loan, CreditCard


class CustomerSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'dob', 'aadhar_number', 'phone_number', 
                  'address', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class AccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    
    class Meta:
        model = Account
        fields = ['id', 'customer', 'customer_name', 'account_number', 'account_type', 
                  'balance', 'status', 'created_at', 'updated_at']
        read_only_fields = ['balance', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'account_number', 'transaction_type', 'amount', 
                  'reference_account', 'created_by', 'created_by_name', 'timestamp']
        read_only_fields = ['created_by', 'timestamp']


class LoanSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    loan_type_display = serializers.CharField(source='get_loan_type_display', read_only=True)
    employment_status_display = serializers.CharField(source='get_employment_status_display', read_only=True)
    
    class Meta:
        model = Loan
        fields = ['id', 'customer', 'customer_name', 'loan_type', 'loan_type_display',
                  'loan_amount', 'interest_rate', 'tenure_months', 'status',
                  'monthly_payment', 'total_interest', 'total_payable',
                  'processing_fee', 'processing_fee_percentage', 'gst_amount', 'gst_percentage',
                  'net_disbursal', 'employment_status', 'employment_status_display',
                  'annual_income', 'employment_duration', 'credit_score',
                  'documents_submitted', 'approved_by', 'approved_by_name',
                  'approval_date', 'rejection_reason', 'created_at', 'updated_at']
        read_only_fields = ['approved_by', 'approval_date', 'created_at', 'updated_at',
                           'monthly_payment', 'total_interest', 'total_payable',
                           'processing_fee', 'gst_amount', 'net_disbursal']


class CreditCardSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = CreditCard
        fields = ['id', 'customer', 'customer_name', 'card_number', 'credit_limit', 
                  'current_outstanding', 'status', 'approved_by', 'approved_by_name', 
                  'created_at', 'updated_at']
        read_only_fields = ['approved_by', 'created_at', 'updated_at']
