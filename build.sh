#!/usr/bin/env bash
set -o errexit

echo "======================================"
echo " Starting Vulcano Build Process"
echo "======================================"

echo ""
echo " Python version:"
python --version

echo ""
echo " Upgrading pip..."
pip install --upgrade pip

echo ""
echo " Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "  Collecting static files..."
python manage.py collectstatic --no-input --clear

echo ""
echo "  Running database migrations..."
python manage.py migrate --noinput

echo ""
echo "======================================"
echo "✅ Build completed successfully!"
echo "======================================"
