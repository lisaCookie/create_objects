#!/bin/bash
set -e

echo "Running database migrations..."
python -m RECIPES.database.db_init

echo "Starting Gunicorn..."
exec gunicorn --config gunicorn.conf.py --bind 0.0.0.0:5000 app:app