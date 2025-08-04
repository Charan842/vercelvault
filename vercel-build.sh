#!/bin/bash

# Exit on any error
set -e

echo "Starting build process..."

# Check Python version
python3 --version

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-vercel.txt

# Set Django settings
export DJANGO_SETTINGS_MODULE=storageproduct.settings

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Build completed successfully!" 