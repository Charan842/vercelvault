#!/usr/bin/env python
"""
Simple test script to verify Vercel configuration
"""
import os
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Test Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storageproduct.settings')

try:
    import django
    django.setup()
    print("✅ Django settings loaded successfully")
    
    from django.conf import settings
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✅ DATABASE: {settings.DATABASES['default']['ENGINE']}")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("🎉 All tests passed! Configuration is ready for Vercel deployment.")
