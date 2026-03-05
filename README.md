- BDE-Prime : Comparateur de Prix Drive

PanierMalin est un outil de web-scraping moderne permettant de comparer en temps réel les prix d'un produit spécifique sur les enseignes Auchan, Carrefour et Intermarché.

Le projet utilise FastAPI pour l'interface web et Playwright pour la navigation automatisée (gestion du JavaScript et des prix dynamiques).
-  Fonctionnalités

    Recherche Multi-sites : Une seule saisie utilisateur lance des recherches simultanées.

    Extraction Dynamique : Capable de lire les prix générés en JavaScript.

    Détection de Promos : Identifie les prix barrés et calcule le pourcentage de remise (en cours).

    Architecture Modulaire : Un fichier par enseigne pour une maintenance facilitée.

    Prêt pour le Cloud : Entièrement conteneurisé avec Docker et Docker Compose.

-  Installation et Lancement
Prérequis

    Docker

    Docker Compose

Démarrage rapide

    Cloner le dépôt :
    Bash

    git clone https://github.com/ton-pseudo/panier-malin.git
    cd panier-malin

    Lancer l'application avec Docker Compose :
    Bash

    docker-compose up --build

    Accéder à l'interface :
    Ouvrez votre navigateur sur http://localhost:8000

- Structure du Projet
Plaintext

.
├── app.py                 # Serveur FastAPI (Points d'entrée API/Web)
├── scrapers/              # Coeur du scraping
│   ├── __init__.py
│   ├── auchan.py          # Logique spécifique Auchan
│   ├── carrefour.py       # Logique spécifique Carrefour
│   └── intermarche.py     # Logique spécifique Intermarché
├── templates/             # Interface utilisateur (HTML/Jinja2)
├── static/                # Assets (CSS/JS)
├── Dockerfile             # Configuration de l'image (Playwright + Python)
├── docker-compose.yml     # Orchestration des services
└── requirements.txt       # Dépendances Python

⚙️ Configuration (Développement)

Si vous souhaitez lancer le projet sans Docker (en local) :

    Créer un environnement virtuel :
    Bash

    python -m venv venv
    source venv/bin/activate  # ou venv\Scripts\activate sur Windows

    Installer les dépendances :
    Bash

    pip install -r requirements.txt
    playwright install chromium

    Lancer le serveur :
    Bash

    uvicorn app:app --reload

- Notes importantes sur le Scraping

    Éthique : Ce script est destiné à un usage personnel et pédagogique. Veillez à ne pas surcharger les serveurs des enseignes (respect du robots.txt).

    Maintenance : Les sites marchands changent souvent leurs balises HTML. Si un scraper ne renvoie plus de prix, vérifiez les sélecteurs CSS dans le dossier scrapers/.

- Roadmap

    [ ] Ajouter la détection automatique des promotions.

    [ ] Calcul du prix au kilo/unité pour une comparaison plus juste.

    [ ] Ajout d'une base de données Redis pour mettre en cache les résultats (1h).

    [ ] Graphique d'historique des prix sur 7 jours.