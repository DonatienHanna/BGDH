# Système d'Analyse et de Signaux de Trading (SAST)

Un système d'analyse technique et de génération de signaux de trading basé sur Django, Python et PostgreSQL.

## BG-DH

<!-- ton message -->

## Vue d'ensemble

Le SAST est une application web qui collecte des données de marché Forex en temps réel, applique des indicateurs techniques personnalisés et génère des signaux de trading selon différentes stratégies. L'application offre un tableau de bord interactif permettant de visualiser les données de marché, les indicateurs techniques et les signaux générés.

<!-- Photo à mettre si t'en as -->

## Fonctionnalités

- **Collecte de données Forex** via Alpha Vantage API
- **Indicateurs techniques** :
  - Bandes de Bollinger (période: 27, déviation: 2.7)
  - Williams %R (période: 75, niveaux: -80/-20)
  - Oscillateur Stochastique (périodes: 40/20/15, niveaux: 20/80)
- **Génération de signaux** basée sur des stratégies individuelles ou combinées
- **Tableau de bord** pour visualiser les données et signaux
- **API REST** pour accéder aux données et signaux
- **Architecture modulaire** avec Django et Celery pour les tâches asynchrones

## Installation

### Prérequis

- Python 3.9+
- PostgreSQL
- Redis (pour Celery)

### Configuration

1. Clonez le dépôt :
```bash
git clone https://github.com/DonatienHanna/BGDH.git
cd BGDH
```

2. Créez et activez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Créez un fichier `.env` à la racine du projet :
```
DB_NAME=trading_signals_db
DB_USER=user
DB_PASSWORD=user123
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-)q9pkf6!ki!#u4h5djnrtp7)f(=29brqxys8p@_om^puqq5cek
ALPHA_VANTAGE_API_KEY=073XRZ4KX6ENI78E
```

Le fichier setup_postgres.sh se charge de la configuration de la base de données et de la table nécessaire au fonctionnement du projet.
Cependant, vous devez vérifier que postgresql est bien installé sur votre ordinateur et si l'utilisateur et le mot de passe associés existent et sont corrects (dans le .env).

5. Configurez la base de données PostgreSQL :
```bash
bash setup_postgres.sh
```

## Démarrage

1. Appliquez les migrations :
```bash
python manage.py migrate
```

2. Créez un superutilisateur :
```bash
python manage.py createsuperuser
```

3. Démarrez le serveur Django :
```bash
python manage.py runserver
```

4. Démarrez le worker Celery (dans un nouveau terminal) :
```bash
celery -A trading_signals_platform worker --loglevel=info
```

5. Démarrez le planificateur Celery Beat (dans un autre terminal) :
```bash
celery -A trading_signals_platform beat --loglevel=info
```

6. Accédez à l'application via http://localhost:8000/

## Utilisation

### Récupération des données de marché

Pour obtenir des données historiques pour une paire de devises :

```python
from market_data.tasks import update_forex_data_task
update_forex_data_task('EURUSD', '1d')  # Pour des données quotidiennes
```

### Génération de signaux

Pour générer des signaux avec la stratégie combinée :

```python
from signals.tasks import generate_combined_strategy_signals_task
generate_combined_strategy_signals_task('EURUSD', '1h')
```

### Interface d'administration

Accédez à l'interface d'administration via http://localhost:8000/admin/ pour gérer les paires de devises, les stratégies et les signaux.

## Structure du projet

```
BGDH/
├── trading_signals_platform/  # Configuration du projet Django
├── market_data/              # Gestion des données de marché
├── signals/                  # Génération et gestion des signaux
├── users/                    # Gestion des utilisateurs
├── dashboard/                # Interface utilisateur
├── manage.py                 # Script de gestion Django
├── setup_postgres.sh         # Script de configuration de PostgreSQL
└── start_services.sh         # Script de démarrage des services
```

## Indicateurs techniques

### Bandes de Bollinger
- **Période** : 27
- **Déviation** : 2.7
- **Décalage** : 0

### Williams %R
- **Période** : 75
- **Niveaux** : -80 (survente) / -20 (surachat)

### Oscillateur Stochastique
- **Période %K** : 40
- **Période %D** : 20
- **Ralentissement** : 15
- **Niveaux** : 20 (survente) / 80 (surachat)

## Stratégie combinée

La stratégie principale combine les trois indicateurs pour générer des signaux :

- **Signal d'achat** : 
  - Le prix touche la bande inférieure de Bollinger
  - Williams %R est en dessous de -80
  - L'oscillateur stochastique croise ses lignes en dessous du niveau 20

- **Signal de vente** : 
  - Le prix touche la bande supérieure de Bollinger
  - Williams %R est au-dessus de -20
  - L'oscillateur stochastique croise ses lignes au-dessus du niveau 80

## Développement futur

Le projet est en constante évolution, avec plusieurs fonctionnalités prévues :
- Amélioration de l'interface utilisateur
- Ajout de nouveaux indicateurs techniques
- Intégration de l'apprentissage automatique pour optimiser les signaux
- Backtesting des stratégies sur données historiques
- Système de notifications par email

## Contact

Donatien Hanna - [donyhanna45@gmail.com](mailto:donyhanna45@gmail.com)

Project Link: [https://github.com/DonatienHanna/BGDH](https://github.com/DonatienHanna/BGDH)
