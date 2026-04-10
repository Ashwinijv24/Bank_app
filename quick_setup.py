#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from staff.models import Staff

print("Creating staff users...")

users = [
    {'username': 'field1', 'password': 'field123', 'email': 'field@bank.com', 'role': 'FIELD', 'employee_id': 'FLD001', 'first_name': 'Field', 'last_name': 'Officer'},
    {'username': 'cse1', 'password': 'cse123', 'email': 'cse@bank.com', 'role': 'CSE', 'employee_id': 'CSE001', 'first_name': 'Customer', 'last_name': 'Service'},
    {'username': 'loan1', 'password': 'loan123', 'email': 'loan@bank.com', 'role': 'LOAN', 'employee_id': 'LN001', 'first_name': 'Loan', 'last_name': 'Officer'},
    {'username': 'manager1', 'password': 'manager123', 'email': 'manager@bank.com', 'role': 'MANAGER', 'employee_id': 'MGR001', 'first_name': 'Branch', 'last_name': 'Manager'},
]

for user_data in users:
    password = user_data.pop('password')
    username = user_data['username']
    try:
        if not Staff.objects.filter(username=username).exists():
            Staff.objects.create_user(password=password, **user_data)
            print(f"✓ Created {username} ({user_data['role']})")
        else:
            print(f"✓ {username} already exists")
    except Exception as e:
        print(f"✗ Error creating {username}: {e}")

print("\n✓ Done! Login credentials:")
print("Field Officer: field1 / field123")
print("CSE: cse1 / cse123")
print("Loan Officer: loan1 / loan123")
print("Manager: manager1 / manager123")
