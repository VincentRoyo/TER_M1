import glob
import pymongo
import pandas as pd
import logging
import time
from scipy.spatial import ConvexHull
import math
import numpy as np

# Logger pour générer un fichier de log
logger = logging.getLogger("")
logging.basicConfig(filename='/app/output/mongo_init.log', level=logging.INFO, format='%(levelname)s :: %(asctime)s :: %(message)s')


"""
Prend une liste de GeoJSON de type Point et retourne un GeoJSON de type Polygon représentant l'enveloppe convexe.
"""
def chansAlgorithm(geojson_list, threshold=3):
    """
    Calcule l'enveloppe convexe d'une liste de points GeoJSON en utilisant
    l'algorithme optimisé de Chan, après avoir éliminé les points trop éloignés
    grâce à une méthode robuste (filtrage par MAD).

    Paramètres:
      - geojson_list : liste de features GeoJSON dont le type est "Point".
      - threshold    : multiplicateur appliqué à la MAD pour définir le seuil d'élimination.
                       (La valeur par défaut est 3.)
                       
    Retourne:
      - Un objet GeoJSON de type "Feature" contenant l'enveloppe convexe sous forme de polygone,
        ou None si le nombre de points restants est insuffisant.
    """
    import math, statistics

    # Extraction des points sous forme de tuples
    points = [tuple(feature["coordinates"]) for feature in geojson_list if feature["type"] == "Point"]
    n = len(points)
    if n < 3:
        return None

    # --- Filtrage robuste des outliers ---
    # Calcul du centre robuste (médiane des coordonnées)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    center = (statistics.median(xs), statistics.median(ys))
    
    # Calcul des distances au centre
    distances = [math.sqrt((p[0] - center[0])**2 + (p[1] - center[1])**2) for p in points]
    
    # Calcul de la médiane des distances et de la MAD
    med_distance = statistics.median(distances)
    abs_devs = [abs(d - med_distance) for d in distances]
    mad = statistics.median(abs_devs)
    
    # Si la MAD est nulle, aucun filtrage n'est appliqué (les points sont très concentrés)
    if mad == 0:
        filtered_points = points
    else:
        filtered_points = [p for p, d in zip(points, distances) if d <= med_distance + threshold * mad]

    # Vérifier qu'il reste au moins 3 points après filtrage
    if len(filtered_points) < 3:
        return None

    # --- Algorithme de Chan pour le calcul de l'enveloppe convexe ---
    def orientation(p, q, r):
        """
        Renvoie un nombre négatif si r est à gauche de la droite (p,q),
        positif si r est à droite, et 0 si les trois points sont colinéaires.
        """
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def monotone_chain(pts):
        """
        Calcule l'enveloppe convexe d'un ensemble de points avec l'algorithme du chainage monotone.
        """
        pts = sorted(set(pts))
        if len(pts) <= 1:
            return pts
        lower = []
        for p in pts:
            while len(lower) >= 2 and orientation(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        upper = []
        for p in reversed(pts):
            while len(upper) >= 2 and orientation(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        return lower[:-1] + upper[:-1]

    filtered_n = len(filtered_points)
    t = 1
    while True:
        m = min(filtered_n, 2**t)  # Taille des groupes
        # Partition des points en groupes de taille m
        groups = [filtered_points[i:i + m] for i in range(0, filtered_n, m)]
        # Calcul de l'enveloppe convexe de chaque groupe par chainage monotone
        group_hulls = [monotone_chain(group) for group in groups if group]
        
        # Recherche de l'enveloppe convexe globale par marche de Jarvis sur les enveloppes de groupe
        start = min(filtered_points, key=lambda p: (p[0], p[1]))
        hull = [start]
        
        for j in range(m):
            candidate = None
            for H in group_hulls:
                for p in H:
                    if p == hull[-1]:
                        continue
                    if candidate is None:
                        candidate = p
                    else:
                        o = orientation(hull[-1], candidate, p)
                        # Si p est plus à gauche que le candidat actuel
                        if o < 0:
                            candidate = p
                        # En cas de colinéarité, choisir le point le plus éloigné
                        elif o == 0:
                            if (p[0] - hull[-1][0])**2 + (p[1] - hull[-1][1])**2 > (candidate[0] - hull[-1][0])**2 + (candidate[1] - hull[-1][1])**2:
                                candidate = p
            if candidate is None:
                break
            if candidate == start:
                hull.append(candidate)
                break
            hull.append(candidate)
        
        if len(hull) <= m:
            break
        t += 1

    # Fermeture du polygone si nécessaire
    if hull[0] != hull[-1]:
        hull.append(hull[0])

    # Conversion du résultat au format GeoJSON
    convex_hull_geojson = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [list(hull)]
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
    convex_hull_geojson = chansAlgorithm(row["geometry"])

    for _, tree in trees.items():
      if tree["properties"]["plot"]["id"] == row["Plot"]:
        tree["properties"]["plot"]["location"] = convex_hull_geojson

  for _, row in grouped_sub_geometry.iterrows():
    convex_hull_geojson = chansAlgorithm(row["geometry"])

    for _, tree in trees.items():
      if tree["properties"]["plot"]["id"] == row["Plot"]:
        if tree["properties"]["plot"]["sub_plot"]["id"] == row["SubPlot"]:
          tree["properties"]["plot"]["sub_plot"]["location"] = convex_hull_geojson

  return trees


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
      convex_hull_geojson = chansAlgorithm(geo_group["geometry"].iloc[0])

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

            convex_hull_geojson = chansAlgorithm(geo_group["geometry"].iloc[0])

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
      convex_hull_geojson = chansAlgorithm(geo_group["geometry"].iloc[0])

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
            
            convex_hull_geojson = chansAlgorithm(geo_group["geometry"].iloc[0])
            
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
