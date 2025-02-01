# 🚀 TER

## 📂 Structure du projet

Le projet est organisé en trois dossiers principaux :

- **`Docker/`** : Contient le fichier `docker-compose.yml` permettant de déployer un environnement avec **MongoDB** et **Mongo Express**.
- **`Python/`** : Contient une application en Python qui insère des données dans MongoDB.
- **`DataForest/`** : Contient les fichiers de données bruts non formatés.

---

## 🐳 Docker
Le dossier **Docker/** contient un fichier `docker-compose.yml` qui initialise :

- Un serveur **MongoDB** pour stocker les données.
- Une interface web **Mongo Express** accessible à l'adresse : [localhost:8081](http://localhost:8081).

### 🔑 Identifiants Mongo Express :
- **Utilisateur** : `admin`
- **Mot de passe** : `password`

### ▶️ Lancer l'environnement Docker
Exécute la commande suivante dans le dossier `Docker/` :
```bash
docker-compose up -d
```
Cela démarre MongoDB et Mongo Express en arrière-plan.

---

## 🐍 Application Python
Le dossier **Python/** contient un script permettant d'insérer des données dans MongoDB.

### ▶️ Exécuter le script Python
1. Installe les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
2. Lance le script :
   ```bash
   python main.py
   ```

---

## 📁 Données brutes
Le dossier **DataForest/** contient des fichiers de données non formatés qui seront traités et insérés dans MongoDB par l'application Python.

---

## ❓ FAQ
### Comment arrêter les conteneurs Docker ?
```bash
docker-compose down
```

### Comment accéder à la base de données MongoDB ?
Tu peux utiliser Mongo Express via [localhost:8081](http://localhost:8081) ou te connecter directement avec un client MongoDB :
```bash
mongo --host localhost --port 27017 -u admin -p password --authenticationDatabase admin
```

---

✨ Bon développement ! 🚀

