#!/bin/bash

# Activer l'environnement virtuel
source venv/bin/activate

# Appliquer les migrations
echo "Applying migrations..."
python manage.py migrate

# Initialiser les données de démo
echo "Initializing demo data..."
python manage.py init_demo_data

# Démarrer Celery worker (en arrière-plan)
echo "Starting Celery worker..."
celery -A trading_signals_platform worker --loglevel=info --detach

# Démarrer Celery beat (en arrière-plan)
echo "Starting Celery beat..."
celery -A trading_signals_platform beat --loglevel=info --detach

# Démarrer le serveur Django
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000