"""import couchdb
import time
import logging

client = couchdb.Server("https://admin:password@localhost:5984/") # lien de la bd
couch_db1 = client["TER1"] # nom de la bd
couch_db2 = client["TER2"]
couch_db3 = client["TER3"]
# Logger pour générer un fichier de log
logger = logging.getLogger("")
logging.basicConfig(filename='/app/output/execution_times.log', level=logging.INFO, format='%(levelname)s :: %(asctime)s :: %(message)s')

# Liste des requêtes à exécuter
queries = {
    "arbres_par_plot_sousplot": lambda: collection.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot" }, "trees": { "$push": "$properties.tree.id" } }},
        { "$count": "total" }
    ]),
    
    "especes_par_plot_sousplot": lambda: collection.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot" }, "species": { "$addToSet": "$properties.tree.species.species" } }},
        { "$count": "total" }
    ]),
    
    "especes_par_plot": lambda: collection.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id" }, "species": { "$addToSet": "$properties.tree.species.species" } }},
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot_sousplot": lambda: collection.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot" }, "species_count": { "$sum": 1 } }},
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot": lambda: collection.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id" }, "species_count": { "$sum": 1 } }},
        { "$count": "total" }
    ]),
    
    "arbres_morts": lambda: collection.aggregate([
        { "$unwind": "$properties.measurements" },
        { "$sort": { "properties.measurements.census.date": -1 }},
        { "$group": { "_id": "$properties.tree.id", "last_status": { "$first": "$properties.measurements.status.alive_code" } }},
        { "$match": { "last_status": False }},
        { "$count": "total" }
    ]),
    
    "arbres_vivants": lambda: collection.aggregate([
        { "$unwind": "$properties.measurements" },
        { "$sort": { "properties.measurements.census.date": -1 }},
        { "$group": { "_id": "$properties.tree.id", "last_status": { "$first": "$properties.measurements.status.alive_code" } }},
        { "$match": { "last_status": True }},
        { "$count": "total" }
    ])
}

# Exécution et mesure des temps
for name, query in queries.items():
    start_time = time.time()
    result = list(query())
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
    print(f"{name}: {duration} ms")

    logger.info(f"{name}: {duration} ms :: Nombre de données récupéré: {result[0]['total']}")

logger.info("")

queries2 = {
    "arbres_par_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": { "plot": "$features.properties.plot.id", "sub_plot": "$features.properties.plot.sub_plot" }, "trees": { "$push": "$features.properties.tree.id" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": { "plot": "$features.properties.plot.id", "sub_plot": "$features.properties.plot.sub_plot" }, "species": { "$addToSet": "$features.properties.tree.species.species" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot": lambda: collection2.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": "$features.properties.plot.id", "species": { "$addToSet": "$features.properties.tree.species.species" } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": { "plot": "$features.properties.plot.id", "sub_plot": "$features.properties.plot.sub_plot" }, "species_count": { "$sum": 1 } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot": lambda: collection2.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": "$features.properties.plot.id", "species_count": { "$sum": 1 } } },
        { "$count": "total" }
    ]),
    
    "arbres_morts": lambda: collection2.aggregate([
        { "$unwind": "$features" },
        { "$sort": { "features.properties.census.date": -1 } },
        { "$group": { "_id": "$features.properties.tree.id", "last_status": { "$first": "$features.properties.status.alive_code" } } },
        { "$match": { "last_status": False } },
        { "$count": "total" }
    ]),
    
    "arbres_vivants": lambda: collection2.aggregate([
        { "$unwind": "$features" },
        { "$sort": { "features.properties.census.date": -1 } },
        { "$group": { "_id": "$features.properties.tree.id", "last_status": { "$first": "$features.properties.status.alive_code" } } },
        { "$match": { "last_status": True } },
        { "$count": "total" }
    ])
}

# Exécution et mesure des temps pour queries2
for name, query in queries2.items():
    start_time = time.time()
    result = list(query())
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
    print(f"{name}: {duration} ms")

    logger.info(f"{name}: {duration} ms :: Nombre de données récupéré: {result[0]['total']}")

print(f"Résultats enregistrés dans {result}")

logger.info("")

queries3 = {
    "arbres_par_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": { "plot_id": "$features.properties.plot_id", "plot_sub_plot": "$features.properties.plot_sub_plot" }, "trees": { "$push": "$features.properties.tree_id" } } },
        { "$count": "total" }
    ]),

    "especes_par_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": { "plot_id": "$features.properties.plot_id", "plot_sub_plot": "$features.properties.plot_sub_plot" }, "species": { "$addToSet": "$features.properties.tree_species_species" } } },
        { "$count": "total" }
    ]),

    "especes_par_plot": lambda: collection3.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": "$features.properties.plot_id", "species": { "$addToSet": "$features.properties.tree_species_species" } } },
        { "$count": "total" }
    ]),

    "nb_especes_par_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": { "plot_id": "$features.properties.plot_id", "plot_sub_plot": "$features.properties.plot_sub_plot" }, "species_count": { "$sum": 1 } } },
        { "$count": "total" }
    ]),

    "nb_especes_par_plot": lambda: collection3.aggregate([
        { "$unwind": "$features" },
        { "$group": { "_id": "$features.properties.plot_id", "species_count": { "$sum": 1 } } },
        { "$count": "total" }
    ]),

    "arbres_morts": lambda: collection3.aggregate([
        { "$unwind": "$features" },
        { "$sort": { "features.properties.census_date": -1 } },
        { "$group": { "_id": "$features.properties.tree_id", "last_status": { "$first": "$features.properties.status_alive_code" } } },
        { "$match": { "last_status": False } },
        { "$count": "total" }
    ]),

    "arbres_vivants": lambda: collection3.aggregate([
        { "$unwind": "$features" },
        { "$sort": { "features.properties.census_date": -1 } },
        { "$group": { "_id": "$features.properties.tree_id", "last_status": { "$first": "$features.properties.status_alive_code" } } },
        { "$match": { "last_status": True } },
        { "$count": "total" }
    ])
}

# Exécution et mesure des temps pour queries2
for name, query in queries3.items():
    start_time = time.time()
    result = list(query())
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
    print(f"{name}: {duration} ms")

    logger.info(f"{name}: {duration} ms :: Nombre de données récupéré: {result[0]['total']}")

print(f"Résultats enregistrés dans {result}")

client.close()"""