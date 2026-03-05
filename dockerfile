# On utilise l'image officielle de Playwright (elle contient déjà Python et les navigateurs)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation des navigateurs nécessaires (Chromium suffit pour Auchan/Carrefour)
RUN playwright install chromium

# Copie du reste du code
COPY . .

# Port exposé par FastAPI
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]