# Utiliser l'image de base Python
FROM python:3.9

# Installer couch
RUN pip install couchdb3 pandas

# Copier les scripts Python dans le conteneur
COPY ../../Python/script-couch.py /app/script-couch.py
#COPY script-couch.py /app/script-couch.py
COPY ../../Python/script-exec-queries-couch.py /app/script-exec-queries-couch.py

COPY ../../Python/DataForest/ /app/DataForest/

# Définir le répertoire de travail
WORKDIR /app

# Lancer le script Python
CMD ["bash", "-c", "python script-couch.py && python script-exec-queries-couch.py"]
#CMD ["python", "script-couch.py"]
