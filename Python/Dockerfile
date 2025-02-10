# Utiliser l'image de base Python
FROM python:3.9

# Installer pymongo
RUN pip install pymongo pandas couchdb

# Copier les scripts Python dans le conteneur
COPY script-mongo.py /app/script-mongo.py
#COPY script-couch.py /app/script-couch.py

COPY ./DataForest/ /app/DataForest/

# Définir le répertoire de travail
WORKDIR /app

# Lancer le script Python
CMD ["python", "script-mongo.py"]
#CMD ["python", "script-couch.py"]
