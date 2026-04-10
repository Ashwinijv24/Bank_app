import os
import sys
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from staff.models import Staff

print("=" * 50)
print("BANK STAFF SYSTEM - DATABASE SETUP")
print("=" * 50)

# Step 1: Run migrations
print("\n[1/3] Running migrations...")
try:
    call_command('migrate', verbosity=0)
    print("✓ Migrations completed")
except Exception as e:
    print(f"✗ Migration error: {e}")

# Step 2: Create tables manually if needed
print("\n[2/3] Checking database tables...")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff_staff'")
    if not cursor.fetchone():
        print("Creating staff_staff table...")
        cursor.execute("""
            CREATE TABLE staff_staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password VARCHAR(128) NOT NULL,
                last_login DATETIME,
                is_superuser BOOLEAN NOT NULL DEFAULT 0,
                username VARCHAR(150) NOT NULL UNIQUE,
                first_name VARCHAR(150) NOT NULL DEFAULT '',
                last_name VARCHAR(150) NOT NULL DEFAULT '',
                email VARCHAR(254) NOT NULL DEFAULT '',
                is_staff BOOLEAN NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                date_joined DATETIME NOT NULL,
                role VARCHAR(20) NOT NULL,
                employee_id VARCHAR(50) NOT NULL UNIQUE,
                department VARCHAR(100) NOT NULL DEFAULT '',
                is_active_staff BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        print("✓ staff_staff table created")
    else:
        print("✓ staff_staff table exists")

# Step 3: Create users
print("\n[3/3] Creating staff users...")
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

print("\n" + "=" * 50)
print("✓ SETUP COMPLETE!")
print("=" * 50)
print("\nTest Credentials:")
print("  Manager:  manager1 / manager123")
print("  Clerk:    clerk1 / clerk123")
print("  Auditor:  auditor1 / auditor123")
print("\nAccess: http://localhost:3000")
print("=" * 50)
