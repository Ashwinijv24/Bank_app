#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

# Run migrations
print("Running migrations...")
call_command('migrate', verbosity=2)

User = get_user_model()

# Create staff users
staff_data = [
    {
        'username': 'manager1',
        'password': 'manager123',
        'email': 'manager@bank.com',
        'role': 'manager',
        'employee_id': 'MGR001',
        'department': 'Management',
    },
    {
        'username': 'clerk1',
        'password': 'clerk123',
        'email': 'clerk@bank.com',
        'role': 'clerk',
        'employee_id': 'CLK001',
        'department': 'Operations',
    },
    {
        'username': 'auditor1',
        'password': 'auditor123',
        'email': 'auditor@bank.com',
        'role': 'auditor',
        'employee_id': 'AUD001',
        'department': 'Audit',
    },
]

print("\nCreating staff users...")
for data in staff_data:
    password = data.pop('password')
    username = data['username']
    
    if User.objects.filter(username=username).exists():
        print(f"✓ {username} already exists")
    else:
        try:
            user = User.objects.create_user(password=password, **data)
            print(f"✓ Created {username}")
        except Exception as e:
            print(f"✗ Error creating {username}: {e}")

print("\n✓ Database setup complete!")
print("\nTest Credentials:")
print("Manager:  manager1 / manager123")
print("Clerk:    clerk1 / clerk123")
print("Auditor:  auditor1 / auditor123")
