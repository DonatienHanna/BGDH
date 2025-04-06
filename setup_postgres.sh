#!/bin/bash

# Charger les variables d'environnement du fichier .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Fichier .env non trouvé, utilisation des valeurs par défaut"
    export DB_NAME="trading_signals_db"
    export DB_USER="trading_user"
    export DB_PASSWORD="your_password"
fi

# Vérifier si PostgreSQL est installé
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Sur Mac, nous n'avons pas besoin de sudo -u postgres, car l'utilisateur par défaut a déjà les droits
# Vérifier si l'utilisateur existe déjà
user_exists=$(psql -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")

if [ "$user_exists" != "1" ]; then
    echo "Création de l'utilisateur $DB_USER..."
    psql -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
else
    echo "L'utilisateur $DB_USER existe déjà."
fi

# Vérifier si la base de données existe déjà
db_exists=$(psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$db_exists" != "1" ]; then
    echo "Création de la base de données $DB_NAME..."
    psql -d postgres -c "CREATE DATABASE $DB_NAME;"
    psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
else
    echo "La base de données $DB_NAME existe déjà."
fi

echo "Configuration PostgreSQL terminée avec succès!"