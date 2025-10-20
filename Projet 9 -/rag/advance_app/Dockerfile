# Utiliser une image Python officielle
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install uv && \
    uv pip install --no-cache-dir -r requirements.txt --system

# Copier le reste du code
COPY . .

# Créer le répertoire pour le vectorstore s'il n'existe pas
RUN mkdir -p ./vectorstore

# Exposer le port utilisé par Chainlit
EXPOSE 8000

# Commande pour lancer l'application
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]