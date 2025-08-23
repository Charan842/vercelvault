#!/usr/bin/env python
"""
Test script to verify all dependencies are installed correctly
"""
import sys

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            module = __import__(package_name)
        else:
            module = __import__(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
        return False

def main():
    """Test all required dependencies"""
    print("Testing dependencies...")
    
    dependencies = [
        ("Django", "django"),
        ("psycopg2", "psycopg2"),
        ("Pillow", "PIL"),
        ("whitenoise", "whitenoise"),
        ("dj-database-url", "dj_database_url"),
        ("gunicorn", "gunicorn"),
    ]
    
    all_passed = True
    for name, module in dependencies:
        if not test_import(name, module):
            all_passed = False
    
    if all_passed:
        print("\n🎉 All dependencies are installed correctly!")
    else:
        print("\n❌ Some dependencies are missing!")
        sys.exit(1)

if __name__ == "__main__":
    main()
