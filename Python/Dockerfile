# Utiliser l'image de base Python
FROM python:3.9

# Installer pymongo
RUN pip install pymongo pandas

# Copier le script Python dans le conteneur
COPY app.py /app/app.py

COPY ./DataForest/ /app/DataForest/

# Définir le répertoire de travail
WORKDIR /app

# Lancer le script Python
CMD ["python", "app.py"]
