#!/usr/bin/env python
"""Complete setup script for Rural Banking System"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from django.core.management import call_command
from staff.models import Staff, Branch
from customers.models import Customer, Account, Loan, CreditCard

print("=" * 60)
print("RURAL BANKING SYSTEM - COMPLETE SETUP")
print("=" * 60)

# Step 1: Create migrations
print("\n[1/5] Creating migrations...")
try:
    call_command('makemigrations', verbosity=0)
    print("✓ Migrations created")
except Exception as e:
    print(f"✗ Error creating migrations: {e}")

# Step 2: Apply migrations
print("\n[2/5] Applying migrations...")
try:
    call_command('migrate', verbosity=0)
    print("✓ Database migrated")
except Exception as e:
    print(f"✗ Error migrating: {e}")

# Step 3: Create branch
print("\n[3/5] Creating branch...")
try:
    if not Branch.objects.exists():
        branch = Branch.objects.create(
            name="Main Branch",
            code="MB001",
            address="Rural Area, District",
            phone="1234567890",
            email="branch@ruralbank.com"
        )
        print("✓ Branch created")
    else:
        branch = Branch.objects.first()
        print("✓ Branch already exists")
except Exception as e:
    print(f"✗ Error creating branch: {e}")
    branch = None

# Step 4: Create staff users
print("\n[4/5] Creating staff users...")
users = [
    {
        'username': 'field1',
        'password': 'field123',
        'email': 'field@bank.com',
        'role': 'FIELD',
        'employee_id': 'FLD001',
        'first_name': 'Field',
        'last_name': 'Officer'
    },
    {
        'username': 'cse1',
        'password': 'cse123',
        'email': 'cse@bank.com',
        'role': 'CSE',
        'employee_id': 'CSE001',
        'first_name': 'Customer',
        'last_name': 'Service'
    },
    {
        'username': 'loan1',
        'password': 'loan123',
        'email': 'loan@bank.com',
        'role': 'LOAN',
        'employee_id': 'LN001',
        'first_name': 'Loan',
        'last_name': 'Officer'
    },
    {
        'username': 'manager1',
        'password': 'manager123',
        'email': 'manager@bank.com',
        'role': 'MANAGER',
        'employee_id': 'MGR001',
        'first_name': 'Branch',
        'last_name': 'Manager'
    },
]

for user_data in users:
    password = user_data.pop('password')
    username = user_data['username']
    try:
        if not Staff.objects.filter(username=username).exists():
            user = Staff.objects.create_user(password=password, **user_data)
            if branch:
                user.branch = branch
                user.save()
            print(f"✓ Created {username} ({user_data['role']})")
        else:
            print(f"✓ {username} already exists")
    except Exception as e:
        print(f"✗ Error creating {username}: {e}")

# Step 5: Display summary
print("\n[5/5] Setup Summary")
print("=" * 60)
print(f"Total Staff: {Staff.objects.count()}")
print(f"Total Customers: {Customer.objects.count()}")
print(f"Total Accounts: {Account.objects.count()}")
print(f"Total Loans: {Loan.objects.count()}")
print(f"Total Credit Cards: {CreditCard.objects.count()}")

print("\n" + "=" * 60)
print("SETUP COMPLETE!")
print("=" * 60)
print("\nLogin Credentials:")
print("-" * 60)
print("Field Officer:  field1 / field123")
print("CSE:            cse1 / cse123")
print("Loan Officer:   loan1 / loan123")
print("Manager:        manager1 / manager123")
print("-" * 60)
print("\nNext Steps:")
print("1. Start backend:  python manage.py runserver")
print("2. Start frontend: cd frontend && npm start")
print("3. Access app:     http://localhost:3000")
print("=" * 60)
