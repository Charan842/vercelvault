#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storageproduct.settings')
django.setup()

# Import Django management command
from django.core.management import execute_from_command_line

# Run collectstatic
execute_from_command_line(['manage.py', 'collectstatic', '--noinput']) 