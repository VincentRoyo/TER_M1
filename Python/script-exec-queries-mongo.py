import pymongo
import time
import logging

client = pymongo.MongoClient("mongodb://admin:password@mongodb:27017/")
db = client["TER"]
collection = db["forest1"]
collection2 = db["forest2"]
collection3 = db["forest3"]

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
        { "$group": { "_id": {"plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot.id" },"species_set": { "$addToSet": "$properties.tree.species.species" }}},
        {"$project": {"_id": 0, "plot_id": "$_id.plot", "sub_plot": "$_id.sub_plot","species_count": { "$size": "$species_set" }}},
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot": lambda: collection.aggregate([
        { "$group": { "_id": "$properties.plot.id", "species_set": {  "$addToSet": "$properties.tree.species.species" }}},
        { "$project": { "_id": 0, "plot_id": "$_id", "species_count": { "$size": "$species_set" }}},
        { "$count": "total" }
    ]),

    "plots_sousplots_location": lambda: collection.aggregate([
        { "$group": { "_id": "$properties.plot.id", "location": { "$first": '$properties.plot.location' }, "sub_plots": { "$addToSet": '$properties.plot.sub_plot' } } },
        { "$project": { '_id': 0, 'plot_id': '$_id', 'location': 1, 'sub_plots': 1 } },
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
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot" : "$properties.plot.id", "sub_plot" : "$properties.trees.features.properties.sub_plot_id"  }, "trees": { "$push": "$properties.trees.features.properties.tree_id" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot" : "$properties.plot.id", "sub_plot" : "$properties.trees.features.properties.sub_plot_id"  }, "species": { "$addToSet": "$properties.trees.features.properties.species.species" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": "$properties.plot.id", "species": { "$addToSet": "$properties.trees.features.properties.species.species" } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot" : "$properties.plot.id", "sub_plot" : "$properties.trees.features.properties.sub_plot_id"  }, "species_set": { "$addToSet": "$properties.trees.features.properties.species.species" } } },
        { "$project": { "_id": 1, "species_count": { "$size": "$species_set" } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": "$properties.plot.id", "species_set": { "$addToSet": "$properties.trees.features.properties.species.species" } } },
        { "$project": { "_id": 1, "species_count": { "$size": "$species_set" } } },
        { "$count": "total" }
    ]),

    "plots_sousplots_location": lambda: collection.aggregate([
        { "$group": { "_id": "$properties.plot.id", "location": { "$first": '$geometry.coordinates' }, "sub_plots": { "$addToSet": '$properties.sub_plots' } } },
        { "$project": { '_id': 0, 'plot_id': '$_id', 'location': 1, 'sub_plots': 1 } },
        { "$count": "total" }
    ]),
    
    "arbres_morts": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$unwind": "$properties.trees.features.properties.measurements" },
        { "$sort": { "properties.trees.features.properties.measurements.census.date": -1 } },
        { "$group": {
            "_id": "$properties.trees.features.properties.tree_id",
            "last_status": { "$first": "$properties.trees.features.properties.measurements.status.alive_code" },
            }
        },
        { "$match": { "last_status": False } },
        { "$count": "total" }
    ]),
    
    "arbres_vivants": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$unwind": "$properties.trees.features.properties.measurements" },
        { "$sort": { "properties.trees.features.properties.measurements.census.date": -1 } },
        { "$group": {
            "_id": "$properties.trees.features.properties.tree_id",
            "last_status": { "$first": "$properties.trees.features.properties.measurements.status.alive_code" },
            }
        },
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
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.trees.features.properties.sub_plot_id" }, "trees": { "$push": "$properties.trees.features.properties.tree_id" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.trees.features.properties.sub_plot_id" }, "species": { "$addToSet": "$properties.trees.features.properties.tree_species_species" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": "$properties.plot.id", "species": { "$addToSet": "$properties.trees.features.properties.tree_species_species" } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.trees.features.properties.sub_plot_id" }, "species_set": { "$addToSet": "$properties.trees.features.properties.tree_species_species" } } },
        { "$project": { "_id": 1, "species_count": { "$size": "$species_set" } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": "$properties.plot.id", "species_set": { "$addToSet": "$properties.trees.features.properties.tree_species_species" } } },
        { "$project": { "_id": 1, "species_count": { "$size": "$species_set" } } },
        { "$count": "total" }
    ]),

    "plots_sousplots_location": lambda: collection.aggregate([
        { "$group": { "_id": "$properties.plot.id", "location": { "$first": '$geometry.coordinates' }, "sub_plots": { "$addToSet": '$properties.sub_plots' } } },
        { "$project": { '_id': 0, 'plot_id': '$_id', 'location': 1, 'sub_plots': 1 } },
        { "$count": "total" }
    ]),

    "arbres_morts": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$sort": { "properties.trees.features.properties.census_date": -1 } },
        { "$group": {
            "_id": "$properties.trees.features.properties.tree_id",
            "last_status": { "$first": "$properties.trees.features.properties.status_alive_code" },
            }
        },
        { "$match": { "last_status": False } },
        { "$count": "total" }
    ]),
    
    "arbres_vivants": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$sort": { "properties.trees.features.properties.census_date": -1 } },
        { "$group": {
            "_id": "$properties.trees.features.properties.tree_id",
            "last_status": { "$first": "$properties.trees.features.properties.status_alive_code" },
            }
        },
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

client.close()