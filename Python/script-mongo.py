import glob
import pymongo
import pandas as pd
import logging
import time
from scipy.spatial import ConvexHull

# Logger pour générer un fichier de log
logger = logging.getLogger("")
logging.basicConfig(filename='/app/output/mongo_init.log', level=logging.INFO, format='%(levelname)s :: %(asctime)s :: %(message)s')


"""
Prend une liste de GeoJSON de type Point et retourne un GeoJSON de type Polygon représentant l'enveloppe convexe.
"""
def grahamScan(geojson_list):
    
    points = [feature["coordinates"] for feature in geojson_list if feature["type"] == "Point"]

    if len(points) < 3:
        return None

    hull = ConvexHull(points)
    hull_points = [points[i] for i in hull.vertices]
    hull_points.append(hull_points[0])

    convex_hull_geojson = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [hull_points]
        },
        "properties": {}
    }

    return convex_hull_geojson

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
      "sub_plot": {
        "id": "SubPlot",
        "location": {
          "type": "Feature",
          "geometry": 
          {
            "type": "Polygon",
            "coordinates": [
              ["Lon","Lat"]
            ]
          } 
        }
      },
      "location": {
        "type": "Feature",
        "geometry": 
        {
          "type": "Polygon",
          "coordinates": [
            [
              ["Lon","Lat"],
              ["Lon","Lat"]
            ]
          ]
        } 
      }
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
                      "sub_plot": {
                          "id": row["SubPlot"]
                      }
                  },
                  "tree": {
                      "field_number": row["TreeFieldNum"],
                      "id": tree_id,
                      "species": {
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
          
          # Ajout conditionnel pour les colonnes suceptibles d'avoir des valeurs indéterminées
          if "Indet." not in row["Family"]:
              trees[tree_id]["properties"]["tree"]["species"]["family"] = row["Family"]
          if "Indet." not in row["Genus"]:
            trees[tree_id]["properties"]["tree"]["species"]["genus"] = row["Genus"]
          if "Indet." not in row["Species"]:
            trees[tree_id]["properties"]["tree"]["species"]["species"] = row["Species"]


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
  

  grouped_geometry = df.groupby("Plot").apply(lambda g: [
    {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
  ]).reset_index(name="geometry")

  grouped_sub_geometry = df.groupby(["Plot", "SubPlot"]).apply(lambda g: [
    {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
  ]).reset_index(name="geometry")


  for _, row in grouped_geometry.iterrows():
    convex_hull_geojson = grahamScan(row["geometry"])

    for _, tree in trees.items():
      if tree["properties"]["plot"]["id"] == row["Plot"]:
        tree["properties"]["plot"]["location"] = convex_hull_geojson

  for _, row in grouped_sub_geometry.iterrows():
    convex_hull_geojson = grahamScan(row["geometry"])

    for _, tree in trees.items():
      if tree["properties"]["plot"]["id"] == row["Plot"]:
        if tree["properties"]["plot"]["sub_plot"]["id"] == row["SubPlot"]:
          tree["properties"]["plot"]["sub_plot"]["location"] = convex_hull_geojson

  return trees


""" TODO pas encore fait l'algo de graham pour cette structure
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        ["Lon", "Lat"],
       ]
    ]
  },
  "properties": {
    "plot": {
      "id": "Plot_ID",
      "area": "PlotArea"
    },
    "sub_plots": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                ["LonSub", "LatSub"],
              ]
            ]
          },
          "properties": {
            "id": "SubPlot_ID"
          }
        }     
      ]
    },
    "trees": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": ["LonTree1", "LatTree1"]
          },
          "properties": {
            "tree_id": "idTree",
            "field_number": "TreeFieldNum",
            "sub_plot_id": "SubPlot_ID", 
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
      ]
    }
  }
}
"""

def transformToJSON2(df):
   plots = {}

   grouped_data = df.groupby(["Plot"])

   grouped_geometry = df.groupby("Plot").apply(lambda g: [
       {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
       ]).reset_index(name="geometry")
   
   grouped_sub_geometry = df.groupby(["Plot", "SubPlot"]).apply(lambda g: [
      {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
      ]).reset_index(name="geometry")

   for plot, group in grouped_data:
      plot_id = plot[0]

      geo_group = grouped_geometry[grouped_geometry["Plot"] == plot_id]
      convex_hull_geojson = grahamScan(geo_group["geometry"].iloc[0])

      plots[plot] = {
          "type": "Feature",
          "geometry": convex_hull_geojson["geometry"],
          "properties": {
              "plot": {
                "id": plot_id,
                "area": group["PlotArea"].iloc[0]
              },
              "sub_plots": {
                "type": "FeatureCollection",
                "features": []
              },
              "trees": {
                "type": "FeatureCollection",
                "features": []
              }
          }         
      }
      
      sub_plots_set = set()
      trees_set = set()

      for _, row in group.iterrows():
         sub_plot_id = row["SubPlot"]
         if sub_plot_id not in sub_plots_set:
            sub_plots_set.add(sub_plot_id)

            geo_group = grouped_sub_geometry [
               (grouped_sub_geometry["Plot"] == plot_id) & (grouped_sub_geometry["SubPlot"] == sub_plot_id)
                ]

            convex_hull_geojson = grahamScan(geo_group["geometry"].iloc[0])

            plots[plot]["properties"]["sub_plots"]["features"].append({
               "type": "Feature",
               "geometry": convex_hull_geojson["geometry"],
               "properties": {
                  "id": sub_plot_id
               }
            })
        
         tree_id = row["idTree"]

         if tree_id not in trees_set:
            trees_set.add(tree_id)

            species = {
               "source": row["BotaSource"],
               "certainty": row["BotaCertainty"] == "VRAI"
            }

            if "Indet." not in row["Family"]:
              species["family"] = row["Family"]
            if "Indet." not in row["Genus"]:
              species["genus"] = row["Genus"]
            if "Indet." not in row["Species"]:
              species["species"] = row["Species"]

            plots[plot]["properties"]["trees"]["features"].append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row["Lon"], row["Lat"]]
                    },
                    "properties": {
                        "tree_id": tree_id,
                        "field_number": row["TreeFieldNum"],
                        "sub_plot_id": row["SubPlot"],
                        "species": species,
                        "vernacular": {
                            "id": row["idVern"],
                            "name": row["VernName"],
                            "commercial_species": row["CommercialSp"] == "VRAI"
                        },
                        "measurements": []
                    }
                })

          # Ajout des mesures de l'arbre dans la bonne entrée
         for tree in plots[plot]["properties"]["trees"]["features"]:
            if tree["properties"]["tree_id"] == tree_id:
                tree["properties"]["measurements"].append({
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

   return plots


"""
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        ["Lon", "Lat"],
       ]
    ]
  },
  "properties": {
    "plot": {
      "id": "Plot_ID",
      "area": "PlotArea"
    },
    "sub_plots": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                ["LonSub", "LatSub"],
              ]
            ]
          },
          "properties": {
            "id": "SubPlot_ID"
          }
        }     
      ]
    },
    "trees": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": ["LonTree1", "LatTree1"]
          },
          "properties": {
            "tree_field_number": "TreeFieldNum",
        	  "tree_id": "idTree",
            "sub_plot_id": "SubPlot_ID", 
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
  }            
}
"""
def transformToJSON3(df):
  plots = {}

  grouped_data = df.groupby(["Plot"])

  grouped_geometry = df.groupby("Plot").apply(lambda g: [
      {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
  ]).reset_index(name="geometry")

  grouped_sub_geometry = df.groupby(["Plot", "SubPlot"]).apply(lambda g: [
      {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
  ]).reset_index(name="geometry")

  for plot, group in grouped_data:
      plot_id = plot[0]

      geo_group = grouped_geometry[grouped_geometry["Plot"] == plot_id]
      convex_hull_geojson = grahamScan(geo_group["geometry"].iloc[0])

      plots[plot] = {
          "type": "Feature",
          "geometry": convex_hull_geojson["geometry"],
          "properties": {
              "plot": {
                  "id": plot_id,
                  "area": group["PlotArea"].iloc[0]
              },
              "sub_plots": {
                  "type": "FeatureCollection",
                  "features": []
              },
              "trees": {
                  "type": "FeatureCollection",
                  "features": []
              }
          }
      }

      sub_plots_set = set()
      for _, row in group.iterrows():
        sub_plot_id = row["SubPlot"]
        
        # Ajout du sous-plot
        if sub_plot_id not in sub_plots_set:
            sub_plots_set.add(sub_plot_id)
            
            geo_group = grouped_sub_geometry[
                (grouped_sub_geometry["Plot"] == plot_id) & (grouped_sub_geometry["SubPlot"] == sub_plot_id)
            ]
            
            convex_hull_geojson = grahamScan(geo_group["geometry"].iloc[0])
            
            plots[plot]["properties"]["sub_plots"]["features"].append({
                "type": "Feature",
                "geometry": convex_hull_geojson["geometry"],
                "properties": {
                    "id": sub_plot_id
                }
            })

        tree_id = row["idTree"]

        species = {
            "source": row["BotaSource"],
            "certainty": row["BotaCertainty"] == "VRAI"
        }

        if "Indet." not in row["Family"]:
            species["family"] = row["Family"]
        if "Indet." not in row["Genus"]:
            species["genus"] = row["Genus"]
        if "Indet." not in row["Species"]:
            species["species"] = row["Species"]

        plots[plot]["properties"]["trees"]["features"].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["Lon"], row["Lat"]]
            },
            "properties": {
                "tree_field_number": row["TreeFieldNum"],
                "tree_id": tree_id,
                "sub_plot_id": row["SubPlot"],
                "tree_species_family": species.get("family", ""),
                "tree_species_genus": species.get("genus", ""),
                "tree_species_species": species.get("species", ""),
                "tree_species_source": species.get("source", ""),
                "tree_species_certainty": species.get("certainty", False),
                "tree_vernacular_id": row["idVern"],
                "tree_vernacular_name": row["VernName"],
                "tree_vernacular_commercial_species": row["CommercialSp"] == "VRAI",
                "census_year": row["CensusYear"],
                "census_date": row["CensusDate"],
                "status_alive_code": row["CodeAlive"] == "VRAI",
                "status_measurement_code": row["MeasCode"],
                "status_circumference_value": row["Circ"],
                "status_circumference_corrected_value": row["CircCorr"],
                "status_circumference_correction_code": row["CorrCode"]
            }
        })

  return plots
  


"""
    Fonction d'insertion des données dans une base de données MongoDB
"""
def insertData():
    try: 
        logger.info("Connecting to MongoDB...")
        mongo_client = pymongo.MongoClient("mongodb://admin:password@mongodb:27017/") # lien de la bd
        mongo_db = mongo_client["TER"] # nom de la bd
        mongo_col1 = mongo_db["forest1"]
        mongo_col2 = mongo_db["forest2"]
        mongo_col3 = mongo_db["forest3"]
        
        mongo_col1.delete_many({})
        mongo_col2.delete_many({})
        mongo_col3.delete_many({})
        
    except Exception as e : 
        logger.error(f"Error while connecting to MongoDB: {e}")



    csv_files = glob.glob("./DataForest/*.csv") 
    logger.info(f"CSV files : {csv_files}")
    
    """Indication du type de certaines colonnes car certaines colonnes contiennes des valeurs mixes"""
    data_type = {
      2: float,
      6: float,
      7: float,
      27: str
    }

    # Dans le cas où les données sont répartis dans plusieurs fichiers CSV
    for file in csv_files :

        logger.info(f"Lecture du fichier CSV : {file}")
        
        try:
            df = pd.read_csv(file, dtype=data_type, decimal=',')
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du CSV : {e}")

        start_time_mappage = time.time()
      
        try:
           firstTrees = transformToJSON(df)
        except Exception as e:
           logger.error(f"Erreur lors du mappage des données #1 : {e}")

        end_time_mappage = time.time()
        duration = round(end_time_mappage - start_time_mappage, 2)  # Temps en s

        logger.info(f"Durée du mappage des données #1 : {duration}s")

        start_time_mappage = time.time()

        try:
           secondTrees = transformToJSON2(df)
        except Exception as e:
           logger.error(f"Erreur lors du mappage des données #2 : {e}")
        
        end_time_mappage = time.time()
        duration = round(end_time_mappage - start_time_mappage, 2)  # Temps en s

        logger.info(f"Durée du mappage des données #2 : {duration}s")

        start_time_mappage = time.time()


        try:
           thirdTrees = transformToJSON3(df)
        except Exception as e:
           logger.error(f"Erreur lors du mappage des données #3 : {e}")
        
        
        end_time_mappage = time.time()
        duration = round(end_time_mappage - start_time_mappage, 2)  # Temps en s

        logger.info(f"Durée du mappage des données #3 : {duration}s")

        try:
            start_time_insert = time.time()

            mongo_col1.insert_many(list(firstTrees.values()))
            logger.info(f"{len(firstTrees)} documents insérés pour la première collection")

            mongo_col2.insert_many(list(secondTrees.values()))
            logger.info(f"{len(secondTrees)} documents insérés pour la deuxième collection")

            mongo_col3.insert_many(list(thirdTrees.values()))
            logger.info(f"{len(thirdTrees)} documents insérés pour la troisième collection")

            end_time_insert = time.time()

            duration = round((end_time_insert - start_time_insert) * 1000, 2)  # Temps en ms
            logger.info(f"Data inserted ! Duration : {duration}ms")
        except Exception as e:
            logger.error(f"Error while inserting data: {e}")


insertData()
