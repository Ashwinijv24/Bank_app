from django.contrib.auth.models import AbstractUser
from django.db import models

class Branch(models.Model):
    """Branch model for multi-branch support"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'branch'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Staff(AbstractUser):
    """Staff model with role-based access for rural banking"""
    ROLE_CHOICES = (
        ('FIELD', 'Field Officer'),
        ('CSE', 'Customer Service Executive'),
        ('LOAN', 'Loan Officer'),
        ('MANAGER', 'Branch Manager'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    employee_id = models.CharField(max_length=50, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='staff')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_active_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff_staff'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_role_display()}"
    
    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
