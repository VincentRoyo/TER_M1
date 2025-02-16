import couchdb3
import time
import logging
import json
import requests

# Connexion à CouchDB
client = couchdb3.Server(
    "http://couchdb:5984",
    user="admin",
    password="password"
)

db_name = "forest1"
try:
    couch_db = client.get(db_name) if db_name in client else client.create(db_name)
except Exception as e:
    logging.error(f"Error while connecting to CouchDB: {e}")
    exit(1)

# Logger
logger = logging.getLogger("")
logging.basicConfig(filename='/app/output/execution_times.log', level=logging.INFO, format='%(levelname)s :: %(asctime)s :: %(message)s')

# 📌 Ajout des vues dans un design document
design_doc = {
    "_id": "_design/forest_views",
    "views": {
        "arbres_par_plot_sousplot": {
            "map": '''
            function(doc) {
                emit({ plot: doc.properties.plot.id, sub_plot: doc.properties.plot.sub_plot }, doc.properties.tree.id);
            }
            ''',
            "reduce": """
            function(keys, values, rereduce) {
                if (rereduce) {
                    return values.reduce(function(a, b) {
                        return a.concat(b);
                    }, []);
                } else {
                    return values;
                }
            }
            """
        },
        "especes_par_plot_sousplot": {
            "map": '''
            function(doc) {
                emit({ plot: doc.properties.plot.id, sub_plot: doc.properties.plot.sub_plot }, doc.properties.tree.species.species);
            }
            ''',
            "reduce": """
            function(keys, values, rereduce) {
                if (rereduce) {
                    return values.reduce(function(a, b) {
                        return a.concat(b);
                    }, []);
                } else {
                    return values;
                }
            }
            """
        },
        "especes_par_plot": {
            "map": '''
            function(doc) {
                emit({ plot: doc.properties.plot.id }, doc.properties.tree.species.species);
            }
            '''
        },
        "nb_especes_par_plot_sousplot": {
            "map": '''
            function(doc) {
                emit({ plot: doc.properties.plot.id, sub_plot: doc.properties.plot.sub_plot }, 1);
            }
            ''',
            "reduce": "_sum"
        },
        "nb_especes_par_plot": {
            "map": '''
            function(doc) {
                emit({ plot: doc.properties.plot.id }, 1);
            }
            ''',
            "reduce": "_sum"
        },
        "arbres_morts": {
            "map": '''
            function(doc) {
                if (doc.properties.measurements) {
                    var last_measurement = doc.properties.measurements[doc.properties.measurements.length - 1];
                    if (last_measurement.status.alive_code === false) {
                        emit(doc.properties.tree.id, 1);
                    }
                }
            }
            '''
        },
        "arbres_vivants": {
            "map": '''
            function(doc) {
                if (doc.properties.measurements) {
                    var last_measurement = doc.properties.measurements[doc.properties.measurements.length - 1];
                    if (last_measurement.status.alive_code === true) {
                        emit(doc.properties.tree.id, 1);
                    }
                }
            }
            '''
        }
    }
}

# 📌 Création du design document dans la base
try:
    if "_design/forest_views" in couch_db:
        logging.info("Design document already exists.")
    else:
        couch_db.save(design_doc)
        logging.info("Design document created.")
except Exception as e:
    logging.error(f"Error while creating design document: {e}")

# 📌 Fonction d'exécution des vues
def execute_view_with_requests(view_name):
    try:
        reduce_param = "&reduce=true" if "reduce" in design_doc["views"].get(view_name, {}) else ""
        group_param = "group=true" if "reduce" in design_doc["views"].get(view_name, {}) else ""
        url = f"{client.url}/{db_name}/_design/forest_views/_view/{view_name}?{group_param}{reduce_param}"
        
        response = requests.get(url, auth=('admin', 'password'))
        
        if response.status_code == 200:
            print(response.json())  # Afficher les données JSON récupérées
            return response.json()["rows"]
        else:
            print(f"Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        logging.error(f"Error while executing query {view_name}: {e}")
        return []

# Liste des requêtes
queries = [
    "arbres_par_plot_sousplot",
    "especes_par_plot_sousplot",
    "especes_par_plot",
    "nb_especes_par_plot_sousplot",
    "nb_especes_par_plot",
    "arbres_morts",
    "arbres_vivants"
]

# Exécution et mesure des temps
for name in queries:
    start_time = time.time()
    result = execute_view_with_requests(name)
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
    logger.info(f"{name}: {duration} ms :: Nombre de données récupérées: {len(result)}")
    print(f"{name}: {duration} ms :: Nombre de données récupérées: {len(result)}")

logging.info("Execution terminée.")