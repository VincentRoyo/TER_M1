import couchdb3
import time
import logging
import json
import requests
import time

# Connexion à CouchDB
client = couchdb3.Server(
    "http://couchdb:5984",
    user="admin",
    password="password"
)

# Liste des bases de données
db_names = ["forest1", "forest2", "forest3"]
databases = {}

# Connexion ou création des bases
for db_name in db_names:
    try:
        databases[db_name] = client.get(db_name) if db_name in client else client.create(db_name)
    except Exception as e:
        logging.error(f"Erreur lors de la connexion à {db_name}: {e}")
        exit(1)

# Logger
logger = logging.getLogger("")
logging.basicConfig(filename='/app/output/execution_times.log', level=logging.INFO, format='%(levelname)s :: %(asctime)s :: %(message)s')

# Ajout des vues dans un design document
design_doc_forest1 = {
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
            ''',
            "reduce": """
            function(keys, values, rereduce) {
                if (rereduce) {
                    // Concaténer et supprimer les doublons
                    return Array.from(new Set(values.flat()));
                } else {
                    return Array.from(new Set(values));
                }
            }
            """
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
                    function parseDate(dateStr) {
                        var parts = dateStr.split('/');
                        return new Date(parts[2], parts[1] - 1, parts[0]); // Création de la date avec le bon format (année, mois, jour)
                    }

                    doc.properties.measurements.sort(function(a, b) {
                        return parseDate(a.census.date) - parseDate(b.census.date); // Tri croissant par date
                    });
          
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
                   function parseDate(dateStr) {
                        var parts = dateStr.split('/');
                        return new Date(parts[2], parts[1] - 1, parts[0]); // Création de la date avec le bon format (année, mois, jour)
                    }

                    doc.properties.measurements.sort(function(a, b) {
                        return parseDate(a.census.date) - parseDate(b.census.date); // Tri croissant par date
                    });
          
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

design_doc_forest2 = {
 "_id": "_design/forest2_views",
    "views": {
        "arbres_par_plot_sousplot": {
            "map": '''
            function (doc) {
              if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
                doc.properties.trees.features.forEach(function(tree) {
                  emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.tree_id);
                });
              }
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
            function (doc) {
              if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
                doc.properties.trees.features.forEach(function(tree) {
                  emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.species.species);
                });
              }
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
            function (doc) {
              if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
                doc.properties.trees.features.forEach(function(tree) {
                  emit(doc.properties.plot.id, tree.properties.species.species);
                });
              }
            }
            ''',
            "reduce": """
           function(keys, values, rereduce) {
                if (rereduce) {
                    // Concaténer et supprimer les doublons
                    return Array.from(new Set(values.flat()));
                } else {
                    return Array.from(new Set(values));
                }
            }
            """
        },
        "nb_especes_par_plot_sousplot": {
            "map": '''
            function (doc) {
              if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
                doc.properties.trees.features.forEach(function(tree) {
                  emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.species.species);
                });
              }
            }
            ''',
            "reduce": """
           function (keys, values, rereduce) {
            var speciesSet = {};
            values.forEach(function(value) {
              if (!rereduce) {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              } else {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              }
            });
           return speciesSet.length;
          }
            """
        },
        "nb_especes_par_plot": {
            "map": '''
            function (doc) {
              if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
                doc.properties.trees.features.forEach(function(tree) {
                  emit(doc.properties.plot.id, tree.properties.species.species);
                });
              }
            }
            ''',
            "reduce": """
           function (keys, values, rereduce) {
            var speciesSet = {};
            values.forEach(function(value) {
              if (!rereduce) {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              } else {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              }
            });
           return speciesSet.length;
          }
            """
        },
         "arbres_morts": {
            "map": '''
           function(doc) {
            if (doc.features) {
              doc.features.forEach(function(feature) {
                feature.properties.trees.features.forEach(function(tree) {
                    tree.properties.measurements.forEach(function(measurement) {
                        var treeKey = tree.properties.tree_id;
                        if (measurement.status.alive_code == 0) {
                        emit(treeKey, {
                            alive_code: measurement.status.alive_code,
                            date: measurement.census.date }
                        });
                        }
                      });
                    });
                  });
                }
            }
            ''', 
            "reduce": '''
              function(keys, values, rereduce) {
                if (rereduce) {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                } else {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                }
              }
            '''
        },
        "arbres_vivants": {
            "map": '''
           function(doc) {
            if (doc.features) {
              doc.features.forEach(function(feature) {
                feature.properties.trees.features.forEach(function(tree) {
                    tree.properties.measurements.forEach(function(measurement) {
                        var treeKey = tree.properties.tree_id;
                        if (measurement.status.alive_code == 1) {
                        emit(treeKey, {
                            alive_code: measurement.status.alive_code,
                            date: measurement.census.date }
                        });
                        }
                      });
                    });
                  });
                }
            }
            ''', 
            "reduce": '''
              function(keys, values, rereduce) {
                if (rereduce) {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                } else {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                }
              }
            '''
        }
        
    }
}

design_doc_forest3 = {
  "_id": "_design/forest3_views",
  "views": {
    "arbres_par_plot_sousplot": {
        "map": '''
        function (doc) {
          if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
            doc.properties.trees.features.forEach(function(tree) {
               emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.tree_id);
            });
          }
        }
        ''',
        "reduce": """
        function(keys, values, rereduce) {
            if (rereduce) {
                return values.reduce(function(a, b) {
                    return a.concat(b);
                }, []);
            } else {
                return Array.from(new Set(values));;
            }
        }
        """
    },
    "especes_par_plot_sousplot": {
      "map": """
       function (doc) {
          if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
            doc.properties.trees.features.forEach(function(tree) {
              emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.tree_species_species);
            });
          }
        }
      """,
      "reduce": """
        function(keys, values, rereduce) {
          if (rereduce) {
            return Array.from(new Set(values.flat()));
          } else {
            return Array.from(new Set(values));
          }
        }
      """
    },
    "especes_par_plot": {
      "map": """
         function (doc) {
          if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
            doc.properties.trees.features.forEach(function(tree) {
              emit(doc.properties.plot.id, tree.properties.tree_species_species);
            });
          }
        }
      """,
      "reduce": """
        function(keys, values, rereduce) {
          if (rereduce) {
            return Array.from(new Set(values.flat()));
          } else {
            return Array.from(new Set(values));
          }
        }
      """
    },
    "nb_especes_par_plot_sousplot": {
       "map": '''
            function (doc) {
              if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
                doc.properties.trees.features.forEach(function(tree) {
                  emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.species.species);
                });
              }
            }
            ''',
            "reduce": """
           function (keys, values, rereduce) {
            var speciesSet = {};
            values.forEach(function(value) {
              if (!rereduce) {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              } else {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              }
            });
           return speciesSet.length;
          }
            """
    },
    "nb_especes_par_plot": {
      "map": '''
            function (doc) {
              if (doc.type === "Feature" && doc.properties && doc.properties.trees) {
                doc.properties.trees.features.forEach(function(tree) {
                  emit(doc.properties.plot.id, tree.properties.tree_species_species);
                });
              }
            }
            ''',
            "reduce": """
           function (keys, values, rereduce) {
            var speciesSet = {};
            values.forEach(function(value) {
              if (!rereduce) {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              } else {
                value.forEach(function(species) {
                  speciesSet[species] = true;
                });
              }
            });
           return speciesSet.length;
          }
            """
    },
    "arbres_vivants" : {
         "map": '''
           function(doc) {
            if (doc.features) {
              doc.features.forEach(function(feature) {
                feature.properties.trees.features.forEach(function(tree) {
                        var treeKey = tree.properties.tree_id;
                        if (tree.status.alive_code == 1) {
                        emit(treeKey, {
                            alive_code: measurement.status.alive_code,
                            date: measurement.census.date }
                        }
                      });
                    });
                  });
                }
            }
            ''', 
            "reduce": '''
              function(keys, values, rereduce) {
                if (rereduce) {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                } else {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                }
              }
            '''
    }, 
    "arbres_morts" : {
         "map": '''
           function(doc) {
            if (doc.features) {
              doc.features.forEach(function(feature) {
                feature.properties.trees.features.forEach(function(tree) {
                        var treeKey = tree.properties.tree_id;
                        if (tree.status.alive_code == 0) {
                        emit(treeKey, {
                            alive_code: measurement.status.alive_code,
                            date: measurement.census.date }
                        }
                      });
                    });
                  });
                }
            }
            ''', 
            "reduce": '''
              function(keys, values, rereduce) {
                if (rereduce) {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                } else {
                  return values.reduce(function(a, b) {
                    return a.date > b.date ? a : b; 
                  });
                }
              }
            '''
    }
  }
}


# Ajouter les design documents aux bases de données
if "_design/forest_views" not in databases["forest1"]:
    databases["forest1"].save(design_doc_forest1)

if "_design/forest2_views" not in databases["forest2"]:
    databases["forest2"].save(design_doc_forest2)

if "_design/forest3_views" not in databases["forest3"]:
    databases["forest3"].save(design_doc_forest3)    

# Fonction d'exécution des vues
def execute_view_with_requests(db_name, design_doc,view_name):
    try:
        if db_name == "forest1":
            design_doc_queries = design_doc_forest1
        elif db_name == "forest2":
            design_doc_queries = design_doc_forest2
        elif db_name == "forest3":
            design_doc_queries = design_doc_forest3
        else:
            raise ValueError(f"Unknown database: {db_name}")
        
        reduce_param = "&reduce=true" if "reduce" in design_doc_queries["views"].get(view_name, {}) else ""
        group_param = "group=true" if "reduce" in design_doc_queries["views"].get(view_name, {}) else ""
        stale_param="&stale=ok"
        url = f"{client.url}/{db_name}/_design/{design_doc}/_view/{view_name}?{group_param}{reduce_param}"
        
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
queries_forest1 = list(design_doc_forest1["views"].keys())
queries_forest2 = list(design_doc_forest2["views"].keys())
queries_forest3 = list(design_doc_forest3["views"].keys())

# Exécution et mesure des temps
for name in queries_forest1:
    start_time = time.time()
    result = execute_view_with_requests("forest1", "forest_views",name)
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
    logger.info(f"forest1 - {name}: {duration} ms :: Nombre de données récupérées: {len(result)}")
    print(f"forest1 - {name}: {duration} ms :: Nombre de données récupérées: {len(result)}")

logger.info("")

for name in queries_forest2:
    start_time = time.time()
    result = execute_view_with_requests("forest2", "forest2_views",name)
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
    logger.info(f"forest2 - {name}: {duration} ms :: Nombre de données récupérées: {len(result)}")
    print(f"forest2 - {name}: {duration} ms :: Nombre de données récupérées: {len(result)}")    

logger.info("")

for name in queries_forest3:
    start_time = time.time()
    result = execute_view_with_requests("forest3", "forest3_views",name)
    end_time = time.time()
    duration = round((end_time - start_time) * 1000, 2)  # Temps en ms
    logger.info(f"forest3 - {name}: {duration} ms :: Nombre de données récupérées: {len(result)}")
    print(f"forest3 - {name}: {duration} ms :: Nombre de données récupérées: {len(result)}")  

logging.info("Execution terminée.")