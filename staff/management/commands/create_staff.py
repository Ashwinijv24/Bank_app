from django.core.management.base import BaseCommand
from staff.models import Staff


class Command(BaseCommand):
    help = 'Create default staff users'

    def handle(self, *args, **kwargs):
        users = [
            {'username': 'manager1', 'password': 'manager123', 'email': 'manager@bank.com',
             'role': 'MANAGER', 'employee_id': 'MGR001', 'first_name': 'Branch', 'last_name': 'Manager'},
            {'username': 'cse1', 'password': 'cse123', 'email': 'cse@bank.com',
             'role': 'CSE', 'employee_id': 'CSE001', 'first_name': 'Customer', 'last_name': 'Service'},
            {'username': 'field1', 'password': 'field123', 'email': 'field@bank.com',
             'role': 'FIELD', 'employee_id': 'FLD001', 'first_name': 'Field', 'last_name': 'Officer'},
            {'username': 'loan1', 'password': 'loan123', 'email': 'loan@bank.com',
             'role': 'LOAN', 'employee_id': 'LN001', 'first_name': 'Loan', 'last_name': 'Officer'},
        ]
        for u in users:
            password = u.pop('password')
            if not Staff.objects.filter(username=u['username']).exists():
                Staff.objects.create_user(password=password, **u)
                self.stdout.write(self.style.SUCCESS(f"Created {u['username']}"))
            else:
                self.stdout.write(f"Already exists: {u['username']}")
