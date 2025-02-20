import glob
import pandas as pd
import couchdb3
import logging

# Logger pour générer un fichier de log
logger = logging.getLogger("")
logging.basicConfig(filename='/app/output/couch_init.log', level=logging.INFO, format='%(levelname)s :: %(asctime)s :: %(message)s')

"""
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [
      "Lon",
      "Lat"
    ]
  },
  "properties": {
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
}
"""
def transformToJSON(df):

  trees = {}
  
  for _, row in df.iterrows():
      tree_id = row["idTree"]
      
      if "Indet." not in row["Family"] and "Indet." not in row["Genus"] and "Indet." not in row["Species"]:
          if tree_id not in trees:
              trees[tree_id] = {
                  "type": "Feature",
                  "geometry": {
                      "type": "Point",
                      "coordinates": [row["Lon"], row["Lat"]]
                  },
                  "properties": {
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
                              "certainty": row["BotaCertainty"] == "VRAI"
                          },
                          "vernacular": {
                              "id": row["idVern"],
                              "name": row["VernName"],
                              "commercial_species": row["CommercialSp"] == "VRAI"
                          }
                      },
                      "measurements": []
                  }
              }
          
          trees[tree_id]["properties"]["measurements"].append({
              "census": {
                  "year": row["CensusYear"],
                  "date": row["CensusDate"],
                  "date_certainty": row["CensusDateCertainty"] == "VRAI"
              },
              "status": {
                  "alive_code": row["CodeAlive"] == "VRAI",
                  "measurement_code": row["MeasCode"],
                  "circumference": {
                      "value": row["Circ"],
                      "corrected_value": row["CircCorr"],
                      "correction_code": row["CorrCode"]
                  }
              }
          })
  
  return trees


"""
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": ["Lon", "Lat"]
      },
      "properties": {
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
    }
  ]
}
"""
def transformToJSON2(df):
  
  feature_collection = {"type": "FeatureCollection", "features": []}
  trees = {}
  
  for _, row in df.iterrows():
      tree_id = row["idTree"]
      
      if "Indet." not in row["Family"] and "Indet." not in row["Genus"] and "Indet." not in row["Species"]:
        trees[tree_id] = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["Lon"], row["Lat"]]
            },
            "properties": {
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
                        "certainty": row["BotaCertainty"] == "VRAI"
                    },
                    "vernacular": {
                        "id": row["idVern"],
                        "name": row["VernName"],
                        "commercial_species": row["CommercialSp"] == "VRAI"
                    }
                },
                "census": {
                    "year": row["CensusYear"],
                    "date": row["CensusDate"],
                    "date_certainty": row["CensusDateCertainty"] == "VRAI"
                },
                "status": {
                    "alive_code": row["CodeAlive"] == "VRAI",
                    "measurement_code": row["MeasCode"],
                    "circumference": {
                        "value": row["Circ"],
                        "corrected_value": row["CircCorr"],
                        "correction_code": row["CorrCode"]
                    }
                }
            }
        }
        feature_collection["features"].append(trees[tree_id])
  
  return feature_collection


"""
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": ["Lon", "Lat"]
      },
      "properties": {
        "forest": "Forest_Name",
        "plot_id": "Plot_ID",
        "plot_area": "PlotArea",
        "plot_sub_plot": "SubPlot",
        "tree_field_number": "TreeFieldNum",
        "tree_id": "idTree",
        "tree_species_family": "Family",
        "tree_species_genus": "Genus",
        "tree_species_species": "Species",
        "tree_species_source": "BotaSource",
        "tree_species_certainty": "BotaCertainty",
        "tree_vernacular_id": "idVern",
        "tree_vernacular_name": "VernName",
        "tree_vernacular_commercial_species": "CommercialSp",
        "census_year": "CensusYear",
        "census_date": "CensusDate",
        "census_date_certainty": "CensusDateCertainty",
        "status_alive_code": "CodeAlive",
        "status_measurement_code": "MeasCode",
        "status_circumference_value": "Circ",
        "status_circumference_corrected_value": "CircCorr",
        "status_circumference_correction_code": "CorrCode"
      }
    }
  ]
}
"""
def transformToJSON3(df):

  feature_collection = {"type": "FeatureCollection", "features": []}
  trees = {}

  for _, row in df.iterrows():
      
      tree_id = row["idTree"]
      
      if "Indet." not in row["Family"] and "Indet." not in row["Genus"] and "Indet." not in row["Species"]:
        trees[tree_id] = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["Lon"], row["Lat"]]
            },
            "properties": {
                "forest": row["Forest"],
                "plot_id": row["Plot"],
                "plot_area": row["PlotArea"],
                "plot_sub_plot": row["SubPlot"],
                "tree_field_number": row["TreeFieldNum"],
                "tree_id": row["idTree"],
                "tree_species_family": row["Family"],
                "tree_species_genus": row["Genus"],
                "tree_species_species": row["Species"],
                "tree_species_source": row["BotaSource"],
                "tree_species_certainty": row["BotaCertainty"] == "VRAI",
                "tree_vernacular_id": row["idVern"],
                "tree_vernacular_name": row["VernName"],
                "tree_vernacular_commercial_species": row["CommercialSp"] == "VRAI",
                "census_year": row["CensusYear"],
                "census_date": row["CensusDate"],
                "census_date_certainty": row["CensusDateCertainty"] == "VRAI",
                "status_alive_code": row["CodeAlive"] == "VRAI",
                "status_measurement_code": row["MeasCode"],
                "status_circumference_value": row["Circ"],
                "status_circumference_corrected_value": row["CircCorr"],
                "status_circumference_correction_code": row["CorrCode"]
            }
        }
        feature_collection["features"].append(trees[tree_id])
  
  return feature_collection
  
  


"""
    Fonction d'insertion des données dans une base de données CouchDB
"""
def insertData():
    try: 
        logging.info("Connecting to CouchDB...")
        client = couchdb3.Server(
            "couchdb:5984",
            user="admin",
            password="password"
        )
        
        db_name1 = "forest1"
        db_name2 = "forest2"
        db_name3 = "forest3"
        
        logging.info(f"Etat de la connexion: {client.up()}")
        couch_db1 = client.get(db_name1) if db_name1 in client else client.create(db_name1)
        couch_db2 = client.get(db_name2) if db_name2 in client else client.create(db_name2)
        couch_db3 = client.get(db_name3) if db_name3 in client else client.create(db_name3)

    except Exception as e : 
        logging.error(f"Error while connecting to CouchDB: {e}")


    csv_files = glob.glob("./DataForest/*.csv") 
    logging.info(f"CSV files : {csv_files}")


    for file in csv_files :

        logging.info(f"Lecture du fichier CSV : {file}")
        df = pd.read_csv(file)

        firstTrees = transformToJSON(df)
        secondTrees = transformToJSON2(df)
        thirdTrees = transformToJSON3(df)

        result1 = list(firstTrees.values())
        result2 = secondTrees
        result3 = thirdTrees
       
      
        try:
            for doc in result1:
                couch_db1.create(doc)
            
            couch_db2.create(result2)
            couch_db3.create(result3)
            logging.info("Data inserted !")
        except Exception as e:
            logging.error(f"Error while inserting data: {e}")


insertData()
