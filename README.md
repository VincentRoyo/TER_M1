# 🚀 TER

## 📂 Structure du projet

Le projet est organisé en trois dossiers principaux :

- **`Docker/`** : Contient le fichier `docker-compose.yml` permettant de déployer un environnement avec **MongoDB** et **Mongo Express**.
- **`Python/`** : Contient une application en Python qui insère des données dans MongoDB.
- **`Python/DataForest/`** : Contient les fichiers de données bruts non formatés.

---

## 🐳 Docker
Le dossier **Docker/** contient un fichier `docker-compose.yml` qui initialise :

- Un serveur **MongoDB** pour stocker les données.
- Une interface web **Mongo Express** accessible à l'adresse : [localhost:8081](http://localhost:8081).
- Un conteneur python insérant les données contenus dans tous les fichiers csv de **Python/DataForest** dans la base mongodb

### 🔑 Identifiants Mongo Express :
- **Utilisateur** : `admin`
- **Mot de passe** : `password`

### ▶️ Lancer l'environnement Docker
Exécute la commande suivante dans le dossier `Docker/` :
```bash
docker-compose up --build
```
Cela démarre MongoDB et Mongo Express avec les données.

---

## 🐍 Application Python
Le dossier **Python/ contient un script **app.py permettant d'insérer des données dans MongoDB.

### ▶️ Exécuter le script Python
- Le script s'éxécute automatiquement dans son conteneur docker lors du lancement du fichier compose.

### ▶️ Que fait le script ?
- Le script python se charge de structurer les données contenus dans les fichiers csv dans le format json prédéfini : (mettre lien rapport ou format json)

---

## 📁 Données brutes
Le dossier **Python/DataForest/** contient des fichiers de données non formatés qui seront traités et insérés dans MongoDB par l'application Python.

---

## ❓ FAQ
### Comment arrêter les conteneurs Docker ?
```bash
docker-compose down
```

### Comment reset les conteneurs Docker ?
```bash
docker rm $(docker ps -a -q)
```

### Comment accéder à la base de données MongoDB ?
En utilisant Mongo Express via [localhost:8081](http://localhost:8081)

---

