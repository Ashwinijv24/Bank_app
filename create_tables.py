#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

print("Running all migrations...")
call_command('migrate', '--run-syncdb', verbosity=2)

print("\nDatabase setup complete!")
