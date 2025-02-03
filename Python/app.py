import glob
import pymongo
import pandas as pd

# activer l'environnement virtuel sur Linux : "source ./Python/venv/Scripts/activate"

# desactiver l'environnement virtuel sur Linux : "source ./Python/venv/Scripts/deactivate"

print("Connecting to MongoDB...")
mongo_client = pymongo.MongoClient("mongodb://admin:password@mongodb:27017/") # lien de la bd
mongo_db = mongo_client["TER"] # nom de la bd
mongo_col = mongo_db["forest"]

csv_files = glob.glob("./DataForest/*.csv") 
print(f"CSV files : {csv_files}")

# Dans le cas où les données sont répartis dans plusieurs fichiers CSV
for file in csv_files :

    print(f"Lecture du fichier CSV : {file}")
    df = pd.read_csv(file)

    trees = {}

    # Parcourir les lignes du DataFrame
    for _, row in df.iterrows():
        tree_id = row["idTree"]
        
        # Si l'arbre n'est pas encore dans le dictionnaire, on l'ajoute
        if tree_id not in trees:
            trees[tree_id] = {
                "forest": row["Forest"],
                "plot": {
                    "id": row["Plot"],
                    "area": row["PlotArea"],
                    "sub_plot": row["SubPlot"]
                },
                "tree": {
                    "field_number": row["TreeFieldNum"],
                    "id": tree_id,
                    "species": {
                        "family": row["Family"],
                        "genus": row["Genus"],
                        "species": row["Species"],
                        "source": row["BotaSource"],
                        "certainty": True if row["BotaCertainty"] == "VRAI" else False
                    },
                    "vernacular": {
                        "id": row["idVern"],
                        "name": row["VernName"],
                        "commercial_species": True if row["CommercialSp"] == "VRAI" else False
                    }
                },
                "location": {
                    "type": "Point",
                    "coordinates": [
                        row["Lon"],
                        row["Lat"]
                    ]
                },
                "measurements": []  # Initialisation de la liste des mesures
            }
        
        # Ajout des mesures à la liste correspondante
        trees[tree_id]["measurements"].append({
            "census": {
                "year": row["CensusYear"],
                "date": row["CensusDate"],
                "date_certainty": True if row["CensusDateCertainty"] == "VRAI" else False
            },
            "status": {
                "alive_code": True if row["CodeAlive"] == "VRAI" else False,
                "measurement_code": row["MeasCode"],
                "circumference": {
                    "value": row["Circ"],
                    "corrected_value": row["CircCorr"],
                    "correction_code": row["CorrCode"]
                }
            }
        })

    result = list(trees.values())
    try:
    	result = mongo_col.insert_many(result)
    	print("Data inserted !")
    except Exception as e:
    	print(f"Error while inserting data: {e}")
    
