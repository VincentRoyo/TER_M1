# Utiliser l'image de base Python
FROM python:3.9

# Installer pymongo
RUN pip install pymongo pandas scipy

# Copier les scripts Python dans le conteneur
COPY ../../Python/script-mongo.py /app/script-mongo.py
#COPY script-couch.py /app/script-couch.py
#COPY ../../Python/script-exec-queries-mongo.py /app/script-exec-queries-mongo.py

COPY ../../Python/DataForest/ /app/DataForest/

# Définir le répertoire de travail
WORKDIR /app

# Lancer le script Python
CMD ["bash", "-c", "python script-mongo.py"]
#CMD ["python", "script-couch.py"]
