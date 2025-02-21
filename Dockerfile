# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de code source dans le conteneur
COPY . .

# Installer python-dotenv et apscheduler
RUN pip install Flask SQLAlchemy apscheduler python-dotenv requests

# Exposer le port que Flask utilise
EXPOSE 5000

# Définir les variables d'environnement
ENV FLASK_APP app.py

# Entrée par défaut pour exécuter l'application Flask
#CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
CMD ["python", "app.py"]