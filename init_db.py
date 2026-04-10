#!/usr/bin/env python
"""
Database initialization script for Bank Staff Management System
Run this after migrations to create initial staff users
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_staff_users():
    """Create initial staff users for testing"""
    
    staff_data = [
        {
            'username': 'manager1',
            'password': 'manager123',
            'email': 'manager@bank.com',
            'first_name': 'John',
            'last_name': 'Manager',
            'role': 'manager',
            'employee_id': 'MGR001',
            'department': 'Management',
        },
        {
            'username': 'clerk1',
            'password': 'clerk123',
            'email': 'clerk@bank.com',
            'first_name': 'Jane',
            'last_name': 'Clerk',
            'role': 'clerk',
            'employee_id': 'CLK001',
            'department': 'Operations',
        },
        {
            'username': 'auditor1',
            'password': 'auditor123',
            'email': 'auditor@bank.com',
            'first_name': 'Bob',
            'last_name': 'Auditor',
            'role': 'auditor',
            'employee_id': 'AUD001',
            'department': 'Audit',
        },
    ]
    
    for data in staff_data:
        password = data.pop('password')
        username = data['username']
        
        try:
            if User.objects.filter(username=username).exists():
                print(f"✓ Staff user '{username}' already exists")
            else:
                user = User.objects.create_user(password=password, **data)
                print(f"✓ Created staff user: {username} ({data['role']})")
        except Exception as e:
            print(f"✗ Error creating {username}: {e}")

if __name__ == '__main__':
    print("Initializing Bank Staff Management System Database...")
    print("-" * 50)
    create_staff_users()
    print("-" * 50)
    print("Database initialization complete!")
    print("\nTest Credentials:")
    print("Manager:  manager1 / manager123")
    print("Clerk:    clerk1 / clerk123")
    print("Auditor:  auditor1 / auditor123")
