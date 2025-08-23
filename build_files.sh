#!/bin/bash
# Build script for Vercel deployment

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Build completed!"