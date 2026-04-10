import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from staff.models import Staff

# Run migrations
print("Creating database tables...")
execute_from_command_line(['manage.py', 'migrate'])

print("\nCreating staff users...")

users = [
    {'username': 'manager1', 'password': 'manager123', 'email': 'manager@bank.com', 'role': 'manager', 'employee_id': 'MGR001'},
    {'username': 'clerk1', 'password': 'clerk123', 'email': 'clerk@bank.com', 'role': 'clerk', 'employee_id': 'CLK001'},
    {'username': 'auditor1', 'password': 'auditor123', 'email': 'auditor@bank.com', 'role': 'auditor', 'employee_id': 'AUD001'},
]

for user_data in users:
    password = user_data.pop('password')
    try:
        if not Staff.objects.filter(username=user_data['username']).exists():
            Staff.objects.create_user(password=password, **user_data)
            print(f"✓ Created {user_data['username']}")
        else:
            print(f"✓ {user_data['username']} already exists")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n✓ Setup complete!")
