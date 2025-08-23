#!/bin/bash

# Install dependencies with verbose output
echo "Installing dependencies..."
pip install -r requirements.txt --verbose

# Verify dj-database-url is installed
echo "Verifying dj-database-url installation..."
python -c "import dj_database_url; print('dj-database-url version:', dj_database_url.__version__)"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo "Vercel build completed!"
