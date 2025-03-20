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
    ]),

    "abondance_especes_plot_sousplot": lambda: collection.aggregate([
        { "$group": { "_id": {"plot_id": "$properties.plot.id","sub_plot_id": "$properties.plot.sub_plot.id","species": "$properties.tree.species.species"},"count_species": { "$sum": 1 }}},
        { "$group": { "_id": {"plot_id": "$_id.plot_id","sub_plot_id": "$_id.sub_plot_id"},"species_counts": {"$push": {"species": "$_id.species","count": "$count_species"}},"total_individuals": { "$sum": "$count_species" }}},
        { "$unwind": "$species_counts" },
        { "$project": { "_id": 0, "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id", "species": "$species_counts.species", "abundance_relative": { "$multiply": [
          { "$divide": ["$species_counts.count", "$total_individuals"] },
          100
        ]}}},
        {"$sort": { "plot_id": 1, "sub_plot_id": 1, "species": 1 }},
        { "$count": "total" }
    ], allowDiskUse=True), 

    "nb_arbres_par_plot_sousplot": lambda: collection.aggregate([
        { "$group": { "_id": { "plot_id": "$properties.plot.id", "sub_plot_id": "$properties.plot.sub_plot.id", "plot_area": { "$toDouble": "$properties.plot.area" } }, "total_trees": { "$sum": 1 } } },
        { "$project": { "_id": 0, "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id", "plot_area": "$_id.plot_area", "tree_density": { "$divide": ["$total_trees", "$_id.plot_area"] } } },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "tauxCroissance_par_especes_plot_sousplot": lambda: collection.aggregate([
        { "$unwind": "$properties.measurements" },
        {
            "$project": {
                "plot_id": "$properties.plot.id",
                "sub_plot_id": "$properties.plot.sub_plot.id",
                "species": "$properties.tree.species.species",
                "tree_id": "$properties.tree.id",
                "year": { "$toInt": "$properties.measurements.census.year" },
                "circumference": { "$toDouble": "$properties.measurements.status.circumference.corrected_value" }
            }
        },
        { "$sort": { "tree_id": 1, "year": 1 } },
        {
            "$group": {
                "_id": {
                "plot_id": "$plot_id",
                "sub_plot_id": "$sub_plot_id",
                "species": "$species",
                "tree_id": "$tree_id"
                },
            "firstYear": { "$first": "$year" },
            "lastYear": { "$last": "$year" },
            "firstCircumference": { "$first": "$circumference" },
            "lastCircumference": { "$last": "$circumference" }
            }
        },
        {
            "$project": {
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id",
                "species": "$_id.species",
                "growth_rate": {
                    "$cond": [
                { "$eq": ["$lastYear", "$firstYear"] },
                None,
                {
                    "$divide": [
                        { "$subtract": ["$lastCircumference", "$firstCircumference"] },
                        { "$subtract": ["$lastYear", "$firstYear"] }
                    ]
                    }
                    ]
                }
            }
        },
        { "$match": { "growth_rate": { "$ne": None, "$gte": 0 } } },
        {
            "$group": {
            "_id": {
                "plot_id": "$plot_id",
                "sub_plot_id": "$sub_plot_id",
                "species": "$species"
            },
            "avg_growth_rate": { "$avg": "$growth_rate" }
            }
        },
        {
            "$project": {
                "_id": 0,
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id",
                "species": "$_id.species",
                "avg_growth_rate": 1
            }
        },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1, "species": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "indice_de_shannon": lambda: collection.aggregate([
        {
            "$group": {
            "_id": {
                "plot_id": "$properties.plot.id",
                "sub_plot_id": "$properties.plot.sub_plot.id",
                "species": "$properties.tree.species.species"
            },
            "count_species": { "$sum": 1 }
            }
        },
        {
            "$group": {
            "_id": {
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id"
            },
            "species_counts": {
                "$push": {
                "species": "$_id.species",
                "count": "$count_species"
                }
            },
            "total_trees": { "$sum": "$count_species" }
            }
        },
        { "$unwind": "$species_counts" },
        {
            "$project": {
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "species": "$species_counts.species",
            "p_i": { "$divide": ["$species_counts.count", "$total_trees"] }
            }
        },
        {
            "$project": {
            "plot_id": 1,
            "sub_plot_id": 1,
            "species": 1,
            "shannon_term": { "$multiply": ["$p_i", { "$ln": "$p_i" }] }
            }
        },
        {
            "$group": {
            "_id": {
                "plot_id": "$plot_id",
                "sub_plot_id": "$sub_plot_id"
            },
            "shannon_index": { "$sum": "$shannon_term" }
            }
        },
        {
            "$project": {
            "_id": 0,
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "shannon_index": { "$multiply": ["$shannon_index", -1] }
            }
        },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1 } },
        { "$count": "total" }
    ])
}

logger.info("RESULTAT PREMIERE STRUCTURE")

# Exécution et mesure des temps
for name, query in queries.items():
    try:
        start_time = time.time()
        result = list(query())
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
        print(f"{name}: {duration} ms")

        logger.info(f"{name}: {duration} ms :: Nombre de données récupéré: {result[0]['total']}")
    except Exception as e:
        logger.error(f"Error while executing query {name}: {e}")


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
    ]),

    "abondance_especes_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot_id": "$properties.plot.id", "sub_plot_id": "$properties.trees.features.properties.sub_plot_id", "species": "$properties.trees.features.properties.species.species" }, "count_species": { "$sum": 1 } } },
        { "$group": { "_id": { "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id" }, "species_counts": { "$push": { "species": "$_id.species", "count": "$count_species" } }, "total_trees": { "$sum": "$count_species" } } },
        { "$unwind": "$species_counts" },
        { "$project": { "_id": 0, "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id", "species": "$species_counts.species", "abundance_relative": { "$multiply": [
          { "$divide": ["$species_counts.count", "$total_trees"] },
          100
        ]}}
        },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1, "species": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "nb_arbres_par_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": { "plot_id": "$properties.plot.id", "sub_plot_id": "$properties.trees.features.properties.sub_plot_id", "plot_area": { "$toDouble": "$properties.plot.area" } }, "total_trees": { "$sum": 1 } } },
        { "$project": { "_id": 0, "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id", "plot_area": "$_id.plot_area", "tree_density": { "$divide": ["$total_trees", "$_id.plot_area"] } } },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "tauxCroissance_par_especes_plot_sousplot": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$unwind": "$properties.trees.features.properties.measurements" },
        {
            "$project": {
                "plot_id": "$properties.plot.id",
                "sub_plot_id": "$properties.trees.features.properties.sub_plot_id",
                "species": "$properties.trees.features.properties.species.species",
                "tree_id": "$properties.trees.features.properties.tree_id",
                "year": { "$toInt": "$properties.trees.features.properties.measurements.census.year" },
                "circumference": { "$toDouble": "$properties.trees.features.properties.measurements.status.circumference.corrected_value" }
            }
        },
        { "$sort": { "tree_id": 1, "year": 1 } },
        {
            "$group": {
                "_id": {
                    "plot_id": "$plot_id",
                    "sub_plot_id": "$sub_plot_id",
                    "species": "$species",
                    "tree_id": "$tree_id"
                },
                "firstYear": { "$first": "$year" },
                "lastYear": { "$last": "$year" },
                "firstCircumference": { "$first": "$circumference" },
                "lastCircumference": { "$last": "$circumference" }
            }
        },
        {
            "$project": {
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id",
                "species": "$_id.species",
                "growth_rate": {
                    "$cond": [
                        { "$eq": ["$lastYear", "$firstYear"] },
                        None,
            {
                    "$divide": [
                        { "$subtract": ["$lastCircumference", "$firstCircumference"] },
                        { "$subtract": ["$lastYear", "$firstYear"] }
                    ]
                    }
                    ]
                }
            }
        },
        { "$match": { "growth_rate": { "$ne": None, "$gte": 0 } } },
        {
            "$group": {
                "_id": {
                    "plot_id": "$plot_id",
                    "sub_plot_id": "$sub_plot_id",
                    "species": "$species"
                },
                "avg_growth_rate": { "$avg": "$growth_rate" }
            }
        },
        {
            "$project": {
                "_id": 0,
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id",
                "species": "$_id.species",
                "avg_annual_growth_rate": "$avg_growth_rate"
            }
        },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1, "species": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "indice_de_shannon": lambda: collection2.aggregate([
        { "$unwind": "$properties.trees.features" },
        {
            "$group": {
            "_id": {
                "plot_id": "$properties.plot.id",
                "sub_plot_id": "$properties.trees.features.properties.sub_plot_id",
                "species": "$properties.trees.features.properties.species.species"
            },
            "count_species": { "$sum": 1 }
            }
        },
        {
            "$group": {
            "_id": {
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id"
            },
            "species_counts": {
                "$push": {
                "species": "$_id.species",
                "count": "$count_species"
                }
            },
            "total_trees": { "$sum": "$count_species" }
            }
        },
        { "$unwind": "$species_counts" },
        {
            "$project": {
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "species": "$species_counts.species",
            "p_i": { "$divide": ["$species_counts.count", "$total_trees"] }
            }
        },
        {
            "$project": {
            "plot_id": 1,
            "sub_plot_id": 1,
            "species": 1,
            "shannon_term": { "$multiply": ["$p_i", { "$ln": "$p_i" }] }
            }
        },
        {
            "$group": {
            "_id": {
                "plot_id": "$plot_id",
                "sub_plot_id": "$sub_plot_id"
            },
            "shannon_index": { "$sum": "$shannon_term" }
            }
        },
        {
            "$project": {
            "_id": 0,
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "shannon_index": { "$multiply": ["$shannon_index", -1] }
            }
        },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1 } },
        { "$count": "total" }
    ])
}

logger.info("RESULTAT DEUXIEME STRUCTURE")

# Exécution et mesure des temps pour queries2
for name, query in queries2.items():
    try:
        start_time = time.time()
        result = list(query())
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
        print(f"{name}: {duration} ms")

        logger.info(f"{name}: {duration} ms :: Nombre de données récupéré: {result[0]['total']}")
    except Exception as e:
        logger.error(f"Error while executing query {name}: {e}")

print(f"Résultats enregistrés dans {result}")

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
    ]),

    "abondance_especes_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": { "_id": "$properties.trees.features.properties.tree_id", "plot_id": { "$first": "$properties.plot.id" }, "sub_plot_id": { "$first": "$properties.trees.features.properties.sub_plot_id" }, "species": { "$first": "$properties.trees.features.properties.tree_species_species" } } },
        { "$group": { "_id": { "plot_id": "$plot_id", "sub_plot_id": "$sub_plot_id", "species": "$species" }, "count_species": { "$sum": 1 } } },
        { "$group": { "_id": { "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id" }, "species_counts": { "$push": { "species": "$_id.species", "count": "$count_species" } }, "total_trees": { "$sum": "$count_species" } } },
        { "$unwind": "$species_counts" },
        { "$project": { "_id": 0, "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id", "species": "$species_counts.species", "abundance_relative": { "$multiply": [
        { "$divide": ["$species_counts.count", "$total_trees"] },
          100
        ]}}},
        { "$sort": { "plot_id": 1, "sub_plot_id": 1, "species": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "nb_arbres_par_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        { "$group": {  "_id": "$properties.trees.features.properties.tree_id", "plot_id": { "$first": "$properties.plot.id" }, "sub_plot_id": { "$first": "$properties.trees.features.properties.sub_plot_id" }, "plot_area": { "$first": { "$toDouble": "$properties.plot.area" } } } },
        { "$group": { "_id": { "plot_id": "$plot_id", "sub_plot_id": "$sub_plot_id", "plot_area": "$plot_area" }, "total_trees": { "$sum": 1 } } }, { "$project": { "_id": 0, "plot_id": "$_id.plot_id", "sub_plot_id": "$_id.sub_plot_id", "plot_area": "$_id.plot_area", "tree_density": { "$divide": ["$total_trees", "$_id.plot_area"] } } },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "tauxCroissance_par_especes_plot_sousplot": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        {
            "$group": {
            "_id": {
                "tree_id": "$properties.trees.features.properties.tree_id",
                "year": { "$toInt": "$properties.trees.features.properties.census_year" }
            },
            "plot_id": { "$first": "$properties.plot.id" },
            "sub_plot_id": { "$first": "$properties.trees.features.properties.sub_plot_id" },
            "species": { "$first": "$properties.trees.features.properties.tree_species_species" },
            "circumference": { "$first": { "$toDouble": "$properties.trees.features.properties.status_circumference_corrected_value" } }
            }
        },
        { "$sort": { "_id.tree_id": 1, "_id.year": 1 } },
        {
        "$group": {
            "_id": {
                "plot_id": "$plot_id",
                "sub_plot_id": "$sub_plot_id",
                "species": "$species",
                "tree_id": "$_id.tree_id"
            },
            "firstYear": { "$first": "$_id.year" },
            "lastYear": { "$last": "$_id.year" },
            "firstCircumference": { "$first": "$circumference" },
            "lastCircumference": { "$last": "$circumference" }
            }
        },
        {
            "$project": {
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "species": "$_id.species",
            "growth_rate": {
                "$cond": [
                { "$eq": ["$lastYear", "$firstYear"] },
                None,
                {
                    "$divide": [
                    { "$subtract": ["$lastCircumference", "$firstCircumference"] },
                    { "$subtract": ["$lastYear", "$firstYear"] }
                    ]
                }
                ]
            }
            }
        },
        { "$match": { "growth_rate": { "$ne": None, "$gte": 0 } } },
        {
            "$group": {
            "_id": {
                "plot_id": "$plot_id",
                "sub_plot_id": "$sub_plot_id",
                "species": "$species"
            },
            "avg_growth_rate": { "$avg": "$growth_rate" }
            }
        },
        {
            "$project": {
            "_id": 0,
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "species": "$_id.species",
            "avg_annual_growth_rate": "$avg_growth_rate"
            }
        },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1, "species": 1 } },
        { "$count": "total" }
    ], allowDiskUse=True),

    "indice_de_shannon": lambda: collection3.aggregate([
        { "$unwind": "$properties.trees.features" },
        {
            "$group": {
            "_id": {
                "tree_id": "$properties.trees.features.properties.tree_id",
                "plot_id": "$properties.plot.id",
                "sub_plot_id": "$properties.trees.features.properties.sub_plot_id",
                "species": "$properties.trees.features.properties.tree_species_species"
            }
            }
        },
        {
            "$group": {
            "_id": {
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id",
                "species": "$_id.species"
            },
            "count_species": { "$sum": 1 }
            }
        },
        {
            "$group": {
            "_id": {
                "plot_id": "$_id.plot_id",
                "sub_plot_id": "$_id.sub_plot_id"
            },
            "species_counts": {
                "$push": {
                "species": "$_id.species",
                "count": "$count_species"
                }
            },
            "total_trees": { "$sum": "$count_species" }
            }
        },
        { "$unwind": "$species_counts" },
        {
            "$project": {
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "species": "$species_counts.species",
            "p_i": { "$divide": ["$species_counts.count", "$total_trees"] }
            }
        },
        {
            "$project": {
            "plot_id": 1,
            "sub_plot_id": 1,
            "species": 1,
            "shannon_term": { "$multiply": ["$p_i", { "$ln": "$p_i" }] }
            }
        },
        {
            "$group": {
            "_id": {
                "plot_id": "$plot_id",
                "sub_plot_id": "$sub_plot_id"
            },
            "shannon_index": { "$sum": "$shannon_term" }
            }
        },
        {
            "$project": {
            "_id": 0,
            "plot_id": "$_id.plot_id",
            "sub_plot_id": "$_id.sub_plot_id",
            "shannon_index": { "$multiply": ["$shannon_index", -1] }
            }
        },
        { "$sort": { "plot_id": 1, "sub_plot_id": 1 } },
        { "$count": "total" }
    ])
}

logger.info("RESULTAT TROISIEME STRUCTURE")

# Exécution et mesure des temps pour queries2
for name, query in queries3.items():
    try:
        start_time = time.time()
        result = list(query())
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
        print(f"{name}: {duration} ms")

        logger.info(f"{name}: {duration} ms :: Nombre de données récupéré: {result[0]['total']}")
    except Exception as e:
        logger.error(f"Error while executing query {name}: {e}")

print(f"Résultats enregistrés dans {result}")

client.close()