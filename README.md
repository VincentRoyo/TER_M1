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
- Un conteneur Python insérant les données contenus dans tous les fichiers CSV de **Python/DataForest** dans la base MongoDB

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
Le dossier **Python/** contient un script **app.py** permettant d'insérer des données dans MongoDB et CouchDB.

### ▶️ Exécuter le script Python
- Le script s'exécute automatiquement dans son conteneur Docker lors du lancement du fichier **`Docker/MongoDB/docker-compose.yml`**.

### ▶️ Que fait le script ?
- Le script Python se charge de structurer les données contenus dans les fichiers CSV dans le format json prédéfini : 

```json
{
  "forest": "Forest_Name",
  "plot": {
    "id": "Plot_ID",
    "area": "PlotArea",
    "sub_plot": "SubPlot"
  },
  "tree": {
    "field_number": "TreeFieldNum",
    "id": "idTree",
    "species": {
      "family": "Family",
      "genus": "Genus",
      "species": "Species",
      "source": "BotaSource",
      "certainty": "BotaCertainty"
    },
    "vernacular": {
      "id": "idVern",
      "name": "VernName",
      "commercial_species": "CommercialSp"
    }
  },
  "location": {
    "type": "Point",
    "coordinates": [
      "Lon",
      "Lat"
    ]
  },
  "measurements": [
    {
      "census": {
        "year": "CensusYear",
        "date": "CensusDate",
        "date_certainty": "CensusDateCertainty"
      },
      "status": {
        "alive_code": "CodeAlive",
        "measurement_code": "MeasCode",
        "circumference": {
          "value": "Circ",
          "corrected_value": "CircCorr",
          "correction_code": "CorrCode"
        }
      }
    }
  ]
}
```

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

