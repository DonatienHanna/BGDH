#!/bin/bash

# Vérifier et configurer PostgreSQL
echo "Vérification et configuration de PostgreSQL..."
bash setup_postgres.sh

# Si la configuration PostgreSQL a échoué, arrêtez le script
if [ $? -ne 0 ]; then
    echo "Échec de la configuration PostgreSQL. Arrêt du déploiement."
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer ou mettre à jour les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate

# Initialiser les données de démo
echo "Initialisation des données de démo..."
python manage.py init_demo_data

# Démarrer Celery worker (en arrière-plan)
echo "Démarrage du worker Celery..."
celery -A trading_signals_platform worker --loglevel=info --detach

# Démarrer Celery beat (en arrière-plan)
echo "Démarrage du scheduler Celery beat..."
celery -A trading_signals_platform beat --loglevel=info --detach

# Démarrer le serveur Django
echo "Démarrage du serveur Django..."
python manage.py runserver 0.0.0.0:8000