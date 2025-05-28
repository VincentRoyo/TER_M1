# 🌳 DataForest

## 📂 Structure du projet

Le projet est organisé en plusieurs dossiers principaux :

- **`Docker/`** : Contient le fichier `docker-compose.yml` permettant de déployer tous les environnements du projet.
- **`Docker/API`** : Contient l'API REST Spring Boot 
- **`Docker/CouchDB`** : Contient la base de données CouchDB
- **`Docker/Locust`** : Contient l'outil de monitoring et de charge de l'API 
- **`Docker/MongoDB`** : Contient la base de données MongoDB
- **`Docker/React`** : Contient l'interface web en React 
- **`Docker/YCSB`** : Contient le projet compilé et décompilé de YCSB, ainsi que les workloads utilisés pour les différents benchmarks. Les résultats sont stockés sosu forme de txt dans le dossier result/
- **`Python/`** : Contient des applications en Python qui insère des données dans MongoDB et CouchDB.
- **`Python/DataForest/`** : Contient les fichiers de données bruts non formatés.

---

## 🐳 Docker

### ▶️ Lancer l'environnement Docker
Exécute la commande suivante dans le dossier `Docker/` :
```bash
docker-compose up --build
```
Une fois l’ensemble des services déployés, vous pouvez accéder aux différentes interfaces via les adresses suivantes :

### 🖥️ Interfaces graphiques

#### 🔑 Identifiants Mongo Express (MongoDB) :
- **Adresse** : [localhost:8081](http://localhost:8081)
- **Utilisateur** : `admin`
- **Mot de passe** : `password`

#### 🔑 Identifiants Fauxton (CouchDB) :
- **Adresse** : [localhost:5984/_utils](http://localhost:5984/_utils)
- **Utilisateur** : `admin`
- **Mot de passe** : `password`

#### 🔑 React :
- **Adresse** : [localhost:3000](http://localhost:3000)

#### 🔑 Locust :
- **Adresse** : [localhost:8089](http://localhost:8089)

### 📋 APIs

#### 🔑 Spring Boot :
- **Adresse** : [localhost:8080](http://localhost:8080)

#### 🔑 cAdvisor :
- **Adresse** : [localhost:8085](http://localhost:8085)
- **Pour récupérer les informations d'un conteneur en particulier** : `http://localhost:8085/api/v1.3/subcontainers/{nom_conteneur}`

---
## 🦗 Locust

Ce projet utilise **Locust** pour simuler des charges sur les composants suivants :

- `CouchdbUser` : pour tester les vues CouchDB
- `MongoUser` : pour tester les requêtes MongoDB
- `ApiUser` : pour tester l'API REST

Après avoir accédé à l'interface de test, plusieurs paramétrages seront demandés.

---

### 🧪 Paramétrage dans l'interface Locust

| Champ                   | Description                                          |
|------------------------|------------------------------------------------------|
| **Number of users**    | Nombre total d’utilisateurs simulés (ex : `30`)      |
| **Spawn rate**         | Nombre d’utilisateurs ajoutés par seconde (ex : `5`) |
| **Host**               | **Ne pas toucher**, définit de base par le conteneur |

---

### 🧩 Sélection des `User Classes`

La première chose que Locust demandera sur l'interface sera le choix des utilisateurs à tester, soit donc :

- `CouchdbUser` : pour tester CouchDB
- `MongoUser` : pour tester MongoDB
- `ApiUser` : pour tester l’API REST

> ✅ Sélectionnez une ou plusieurs classes selon la base que vous souhaitez tester.

---

### ⚖️ Répartition des utilisateurs

Par défaut, **Locust répartit équitablement les utilisateurs** entre les classes sélectionnées.

**Exemple :**
- 30 utilisateurs
- 3 classes sélectionnées

Chaque classe recevra automatiquement **10 utilisateurs**.

---

#### 🛠 Modifier les poids dans l’interface

Cliquez sur **l’icône d'engrenage ⚙️** à droite de chaque classe d'utilisateur (dans la liste des "User Classes") pour définir un **poids personnalisé**.

**Le poids contrôle la proportion de chaque classe :**
- CouchdbUser → poids 3
- MongoUser → poids 1
- ApiUser → poids 1

➡️ Cela signifie que pour 50 utilisateurs :
- CouchdbUser → ~30 utilisateurs
- MongoUser → ~10 utilisateurs
- ApiUser → ~10 utilisateurs

---

### ⚙️ Requêtes personnalisées

Pour limiter le nombre de requêtes exécutées par utilisateur :

Cliquer sur le bouton "**Show optional arguments**"

Renseigner :

- `--query-count` : Nombre de requêtes à exécuter par type de requête (ex : `--query-count 20` lancera `20*nbrRequêteWorkload*nbrUser` pour chaque type de **User** coché)

---

### 🧠 Modifier les tests Locust

Chaque type de test (MongoDB, CouchDB, API REST) est implémenté dans un fichier Python spécifique. Vous pouvez facilement modifier ou ajouter de nouveaux scénarios de test en suivant les instructions ci-dessous.

---

#### 🧾 Localisation des scripts

| Type de test | Fichier principal                         | Fichier des requêtes associées              |
|--------------|-------------------------------------------|---------------------------------------------|
| MongoDB      | `Docker/Locust/Mongo/locust_mongo.py`     | `Docker/Locust/Mongo/Workloads/forestX.py`       |
| CouchDB      | `Docker/Locust/Couchdb/locust_couchdb.py` | `Docker/Locust/Couchdb/Workloads/forestX.py`     |
| API REST     | `Docker/Locust/Api/locust_api.py`         | _(Les requêtes sont directement codées dans la classe)_         |

---

#### 🧩 Modifier les requêtes API

Le test de l’API REST utilise directement les routes codées dans la classe `ApiUser` (pas de workloads séparés).

Chaque tâche (`@task(...)`) appelle une route spécifique avec un poids. Exemple :

```python
@task(3)
def get_plot_info(self):
    plot = random.choice(plot_ids)
    self.client.get(f"/infoplot/{plot}", name="/infoplot/:idPlot")
```

> Pour ajouter ou modifier une route, il suffit d’éditer ou ajouter une nouvelle méthode dans cette classe.

Les paramètres (`plot`, `subplot`) sont extraits dynamiquement à partir d’un fichier CSV (`forest.csv`) chargé au démarrage du script.

---

#### 🔁 Ajouter ou modifier une requête MongoDB

Les requêtes MongoDB sont regroupées dans des fichiers par base (forest1, forest2, forest3).

Les requêtes sont retournées sous forme de dictionnaire avec des lambdas dans la fonction `get_queries(...)` :

```python
def get_queries(collection):
    return {
        "especes_par_plot": lambda: collection.aggregate([...]),
        "plots_sousplots_location": lambda: collection.aggregate([...]),
    }
```

> Pour ajouter une requête MongoDB, il suffit d'ajouter une entrée dans la fonction `get_queries`
---

#### 🔁 Ajouter ou modifier une requête CouchDB

Les vues CouchDB sont regroupées dans des fichiers par base (forest1, forest2, forest3).

Chaque vue est décrite dans le dictionnaire `views_forestX` avec une fonction `map` (obligatoire) et une fonction `reduce` (optionnelle mais recommandée pour les agrégations) :

```python
views_forest1 = {
    "especes_par_plot": {
        "map": "function(doc) { emit([doc.properties.plot.id], doc.properties.tree.species.species); }",
        "reduce": "function(keys, values, rereduce) { var s = new Set(values); return Array.from(s); }"
    }
}
```

> Pour ajouter une vue CouchDB, il suffit d'ajouter une entrée dans le dictionnaire


___
## ❕YCSB  

### ▶️ Benchmark classique

Pour lancer un benchmark avec le CoreWorkload (tester sur un jeu de données créé par YCSB), il suffit de rajouter dans `YCSB-compile/workloads` un workload :

CouchDB (exemple) :
```
# Un nombre de documents max qui sera lu
recordcount=1000
# Le nombre d'opérations qui sera réalisé
operationcount=1000
workload=site.ycsb.workloads.CoreWorkload

readallfields=true

# Proportion d'opérations (le total doit faire 1)
readproportion=1
updateproportion=0
scanproportion=0
insertproportion=0

requestdistribution=zipfian
couchdb.host=couchdb1
```

MongoDB (exemple):
```
# Un nombre de documents max qui sera lu
recordcount=1000
# Le nombre d'opérations qui sera réalisé
operationcount=1000
workload=site.ycsb.workloads.CoreWorkload

readallfields=true

# Proportion d'opérations (le total doit faire 1)
readproportion=1
updateproportion=0
scanproportion=0
insertproportion=0

requestdistribution=zipfian
```

#### ⚠️ Si vous voulez tester un benchmark avec CouchDB et MongoDB, il faut créer deux workloads

Ensuite pour que le workload soit exécuté, il suffit de rajouter dans `script.sh`, les commandes :

CouchDB :
```
./YCSB-compile/bin/ycsb.sh load couchdb -s -P YCSB-compile/workloads/un_workload_couchdb
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/un_workload_couchdb > /app/result/un_fichier_couch.txt
```

MongoDB (exemple pour forest1) :
```
./YCSB-compile/bin/ycsb.sh load mongodb -s -P YCSB-compile/workloads/un_workload_mongodb -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=test
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/un_workload_mongodb -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=test > /app/result/un_fichier_mongo.txt
```

### ▶️ Benchmark custom
Pour lancer un benchmark avec le CustomWorkload (tester sur nos données), il suffit de rajouter dans `YCSB-compile/workloads` un workload :

CouchDB (exemple pour forest1):
```
# Un nombre de documents max qui sera lu
recordcount=60801 
# Le nombre d'opérations qui sera réalisé
operationcount=60801 
workload=site.ycsb.workloads.CustomWorkload

readallfields=true

# Proportion d'opérations (le total doit faire 1)
readproportion=0.25
updateproportion=0.75
scanproportion=0
insertproportion=0

requestdistribution=zipfian 
# Ce fichier est créé automatiquement à la fin du script d'insertion des données
customkey.file=/ExtractIds/CouchDB/forest1_ids.txt 
couchdb.host=couchdb1
```

MongoDB (exemple pour forest1):
```
# Un nombre de documents max qui sera lu
recordcount=60801 
# Le nombre d'opérations qui sera réalisé
operationcount=60801 
workload=site.ycsb.workloads.CustomWorkload

readallfields=true

# Proportion d'opérations (le total doit faire 1)
readproportion=0.25
updateproportion=0.75
scanproportion=0
insertproportion=0

requestdistribution=zipfian
# Ce fichier est créé automatiquement à la fin du script d'insertion des données
customkey.file=/ExtractIds/MongoDB/forest1_ids.txt
collection=forest1
```

#### ⚠️ Si vous voulez tester un benchmark avec CouchDB et MongoDB, il faut créer deux workloads


Ensuite pour que le workload soit exécuté, il suffit de rajouter dans `script.sh`, les commandes :

CouchDB (exemple pour forest1) :
```
./YCSB-compile/bin/ycsb.sh run couchdb -s -P YCSB-compile/workloads/un_workload_couch > /app/result/un_fichier_couch.txt
```

MongoDB (exemple pour forest1) :
```
./YCSB-compile/bin/ycsb.sh run mongodb -s -P YCSB-compile/workloads/un_workload_mongo -p mongodb.url="mongodb://admin:password@mongodb:27017/TER?authSource=admin" -p mongodb.database=TER -p mongodb.collection=forest1 > /app/result/un_fichier_mongo.txt
```

### ➕ Ajouter un nouveau comportement de workload

Pour modifier le comportement de YCSB (comme ce qui est fait avec la classe 'CustomWorkload'), il faut se rendre dans le dossier
YSCB-decompile/core/src/main/java/site/ycsb/workloads, puis ajouter une classe qui étend 'CoreWorkload'.

Une fois la classe développée, il est nécessaire de la compiler (à partir de 'YCSB-compile/lib') :

```
javac -cp .\core-0.17.0.jar -d custom_classes chemin\vers\nouvelle\classe\CustomWorkload.java
```

La commande a pour effet de compiler la classe, et de mettre le fichier dans un dossier 'custom_classes' de 'YCSB-compile/lib'.

Maintenant, il faut ajouter cette classe compilée à l'exécutable jar du coeur déjà compilé (cela évite de tout recompilé) :

```
jar uf ./core-0.17.0.jar -C custom_classes site/ycsb/workloads/CustomWorkload.class
```

Enfin, pour utiliser ce nouveau comportement dans un benchmark, il faut modifier les fichiers de workload et mettre le nom de la nouvelle classe dans la propriété 'workload'.

---
## 🍃 Spring Boot

| Méthode | Endpoint                        | Description                                                                 | Paramètres                        | Réponse                    |
|---------|----------------------------------|-----------------------------------------------------------------------------|-----------------------------------|----------------------------|
| GET     | `/all`                          | Retourne toutes les entités `Feature` complètes.                           | _Aucun_                           | `List<Feature>`           |
| GET     | `/allgeo`                       | Retourne toutes les entités au format GeoJSON.                             | _Aucun_                           | `List<Feature>` (GeoJSON) |
| GET     | `/geoplot`                      | Retourne la géolocalisation de chaque `Plot` et leurs `SubPlot`.           | _Aucun_                           | `List<PlotLocationResponse>` |
| GET     | `/infoplot/{idPlot}`           | Retourne les informations complètes d’un plot donné.                       | `idPlot` (String)                | `InfosPlot`               |
| GET     | `/infoplot/{idPlot}/{idSubPlot}` | Retourne les informations d’une sous-parcelle précise dans un plot.        | `idPlot` (String), `idSubPlot` (Integer) | `InfosSubPlot` |


---

## 🐍 Application Python
Le dossier **Python/** contient deux scripts **script-mongo.py** et **script-couch.py** permettant d'insérer des données dans MongoDB et CouchDB.

### ▶️ Exécuter les scripts Python
- Les script s'exécutent automatiquement dans leur conteneur Docker lors du lancement du fichier **`Docker/MongoDB/docker-compose.yml`**.

### ▶️ Que font les scripts ?
- Les scripts Python se chargent de structurer les données contenus dans les fichiers CSV au format JSON prédéfini.

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

---

