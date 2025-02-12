import pymongo
import time

client = pymongo.MongoClient("mongodb://admin:password@mongodb:27017/")
db = client["TER"]
collection = db["forest1"]

# Fichier pour stocker les résultats
output_file = "/app/output/execution_times.txt"

# Liste des requêtes à exécuter
queries = {
    "arbres_par_plot_sousplot": lambda: collection.aggregate([ { "$group": { "_id": { "plot": "$properties.plot.id", "sub_plot": "$properties.plot.sub_plot" }, "trees": { "$push": "$properties.tree.id" } } } ]),
    "especes_par_plot_sousplot": lambda: collection.aggregate([
        { 
            "$group": { 
                "_id": { 
                    "plot": "$properties.plot.id", 
                    "sub_plot": "$properties.plot.sub_plot" 
                }, 
                "species": { 
                    "$addToSet": "$properties.tree.species.species" 
                } 
            } 
        }
    ]),
    
    "especes_par_plot": lambda: collection.aggregate([
        { 
            "$group": { 
                "_id": { 
                    "plot": "$properties.plot.id"
                }, 
                "species": { 
                    "$addToSet": "$properties.tree.species.species" 
                } 
            } 
        }
    ]),
    
    "nb_especes_par_plot_sousplot": lambda: collection.aggregate([
        { 
            "$group": { 
                "_id": { 
                    "plot": "$properties.plot.id", 
                    "sub_plot": "$properties.plot.sub_plot" 
                },
                "species_count": { 
                    "$sum": 1 
                } 
            } 
        }
    ]),
    
    "nb_especes_par_plot": lambda: collection.aggregate([
        { 
            "$group": { 
                "_id": { 
                    "plot": "$properties.plot.id" 
                },
                "species_count": { 
                    "$sum": 1 
                } 
            } 
        }
    ]),
    
    "arbres_morts": lambda: collection.find(
        { "properties.measurements.status.alive_code": False },
        { "properties.tree.id": 1, "_id": 0 }
    ),
    
    "arbres_vivants": lambda: collection.find(
        { "properties.measurements.status.alive_code": True },
        { "properties.tree.id": 1, "_id": 0 }
    ),
    
    "arbres_morts_derniere_date": lambda: collection.aggregate([
        { "$unwind": "$properties.measurements" },
        { "$sort": { "properties.measurements.census.date": -1 } },
        { 
            "$group": { 
                "_id": "$properties.tree.id", 
                "last_status": { "$first": "$properties.measurements.status.alive_code" } 
            } 
        },
        { 
            "$match": { "last_status": False } 
        }
    ]),
    
    "arbres_vivants_derniere_date": lambda: collection.aggregate([
        { "$unwind": "$properties.measurements" },
        { "$sort": { "properties.measurements.census.date": -1 } },
        { 
            "$group": { 
                "_id": "$properties.tree.id", 
                "last_status": { "$first": "$properties.measurements.status.alive_code" } 
            } 
        },
        { 
            "$match": { "last_status": True } 
        }
    ])
}

# Exécution et mesure des temps
with open(output_file, "w") as f:
    for name, query in queries.items():
        start_time = time.time()
        list(query())
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
        f.write(f"{name}: {duration} ms\n")
        print(f"{name}: {duration} ms")

print(f"Résultats enregistrés dans {output_file}")

client.close()