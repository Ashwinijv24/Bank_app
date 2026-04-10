from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

Staff = get_user_model()


class Customer(models.Model):
    """Customer model for rural banking"""
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    dob = models.DateField()
    aadhar_number = models.CharField(max_length=12, unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    
    # Metadata
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='customers_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.aadhar_number})"


class Account(models.Model):
    """Account model"""
    ACCOUNT_TYPE_CHOICES = (
        ('Savings', 'Savings'),
        ('Current', 'Current'),
    )
    
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'account'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account_number} - {self.customer.full_name}"


class Transaction(models.Model):
    """Transaction model for account operations"""
    TRANSACTION_TYPE_CHOICES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    reference_account = models.CharField(max_length=20, null=True, blank=True)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='transactions_created')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transaction'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.timestamp.date()}"


class Loan(models.Model):
    """Comprehensive Loan model with all features"""
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    )
    
    LOAN_TYPE_CHOICES = (
        ('personal', 'Personal Loan'),
        ('auto', 'Auto Loan'),
        ('home', 'Home Loan'),
        ('business', 'Business Loan'),
        ('education', 'Education Loan'),
        ('emergency', 'Emergency Loan'),
    )
    
    EMPLOYMENT_STATUS_CHOICES = (
        ('employed_full', 'Employed (Full-time)'),
        ('employed_part', 'Employed (Part-time)'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
        ('disability', 'Disability Benefits'),
    )
    
    # Basic Information
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES, default='personal')
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Financial Calculations
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_interest = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_payable = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Processing Fees
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    processing_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    gst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_disbursal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Employment & Eligibility
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True)
    annual_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    employment_duration = models.IntegerField(default=0, help_text='Duration in months')
    credit_score = models.IntegerField(null=True, blank=True)
    
    # Documents
    documents_submitted = models.TextField(blank=True, help_text='Comma-separated list of documents')
    
    # Approval
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='loans_approved')
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loan'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_loan_type_display()} - {self.customer.full_name} - {self.status}"
    
    def calculate_emi(self):
        """Calculate EMI using formula: EMI = P × r × (1+r)^n / ((1+r)^n – 1)"""
        from decimal import Decimal
        import math

        P = float(self.loan_amount)
        annual_rate = float(self.interest_rate) / 100
        r = annual_rate / 12
        n = self.tenure_months

        if r == 0:
            emi = P / n
        else:
            emi = P * r * math.pow(1 + r, n) / (math.pow(1 + r, n) - 1)

        self.monthly_payment = Decimal(str(round(emi, 2)))
        self.total_payable   = Decimal(str(round(emi * n, 2)))
        self.total_interest  = self.total_payable - self.loan_amount

    def calculate_fees(self):
        """Calculate processing fee, GST, and net disbursal"""
        from decimal import Decimal
        loan  = Decimal(str(self.loan_amount))
        pfee  = (loan * Decimal('2')) / Decimal('100')
        gst   = (pfee * Decimal('18')) / Decimal('100')
        self.processing_fee = pfee
        self.gst_amount     = gst
        self.net_disbursal  = loan - pfee - gst
    
    def save(self, *args, **kwargs):
        # Auto-calculate EMI and fees before saving
        self.calculate_emi()
        self.calculate_fees()
        super().save(*args, **kwargs)


class CreditCard(models.Model):
    """Credit Card model"""
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Blocked', 'Blocked'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='credit_cards')
    card_number = models.CharField(max_length=16, unique=True)
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    current_outstanding = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_cards_approved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'credit_card'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.card_number} - {self.customer.full_name}"

