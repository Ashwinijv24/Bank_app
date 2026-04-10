from django.db import models
from django.contrib.auth import get_user_model

Staff = get_user_model()

class CreditCardApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    CARD_TYPE_CHOICES = (
        ('basic', 'Basic Card'),
        ('premium', 'Premium Card'),
        ('platinum', 'Platinum Card'),
    )
    
    applicant_name = models.CharField(max_length=200)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=15)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(default="INR", max_length=10)
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    processed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'creditcard_application'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.applicant_name} - {self.get_card_type_display()}"
