import pymongo
import time
import logging

client = pymongo.MongoClient("mongodb://admin:password@mongodb:27017/")
db = client["TER"]
collection = db["forest1"]
collection2 = db["forest2"]

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
        { "$match": { "properties.measurements.status.alive_code": False }},
        { "$count": "total" }
    ]),
    
    "arbres_vivants": lambda: collection.aggregate([
        { "$match": { "properties.measurements.status.alive_code": True }},
        { "$count": "total" }
    ]),
    
    "arbres_morts_derniere_date": lambda: collection.aggregate([
        { "$unwind": "$properties.measurements" },
        { "$sort": { "properties.measurements.census.date": -1 }},
        { "$group": { "_id": "$properties.tree.id", "last_status": { "$first": "$properties.measurements.status.alive_code" } }},
        { "$match": { "last_status": False }},
        { "$count": "total" }
    ]),
    
    "arbres_vivants_derniere_date": lambda: collection.aggregate([
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
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot" }, "trees": { "$push": "$properties.tree.id" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot_sousplot": lambda: collection2.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot" }, "species": { "$addToSet": "$properties.tree.species.species" } } },
        { "$count": "total" }
    ]),
    
    "especes_par_plot": lambda: collection2.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id" }, "species": { "$addToSet": "$properties.tree.species.species" } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot_sousplot": lambda: collection2.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot" }, "species_count": { "$sum": 1 } } },
        { "$count": "total" }
    ]),
    
    "nb_especes_par_plot": lambda: collection2.aggregate([
        { "$group": { "_id": { "plot": "$properties.plot.id" }, "species_count": { "$sum": 1 } } },
        { "$count": "total" }
    ]),
    
    "arbres_morts": lambda: collection2.aggregate([
        { "$match": { "properties.status.alive_code": False } },
        { "$count": "total" }
    ]),
    
    "arbres_vivants": lambda: collection2.aggregate([
        { "$match": { "properties.status.alive_code": True } },
        { "$count": "total" }
    ]),
    
    "arbres_morts_derniere_date": lambda: collection2.aggregate([
        { "$sort": { "properties.census.date": -1 } },
        { "$group": { "_id": "$properties.tree.id", "last_status": { "$first": "$properties.status.alive_code" } } },
        { "$match": { "last_status": False } },
        { "$count": "total" }
    ]),
    
    "arbres_vivants_derniere_date": lambda: collection2.aggregate([
        { "$sort": { "properties.census.date": -1 } },
        { "$group": { "_id": "$properties.tree.id", "last_status": { "$first": "$properties.status.alive_code" } } },
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

client.close()