import glob
import pandas as pd
import logging
import requests
import json
import time
from scipy.spatial import ConvexHull

# Logger
logging.basicConfig(filename='/app/output/couch_init.log', level=logging.INFO,
                    format='%(levelname)s :: %(asctime)s :: %(message)s')

COUCHDB_URL = "http://admin:password@couchdb1:5984"
HEADERS = {"Content-Type": "application/json"}


def init_cluster():
    logging.info("🔧 Initialisation du cluster CouchDB...")

    base_url = COUCHDB_URL
    headers = HEADERS

    try:
        res = requests.post(f"{base_url}/_cluster_setup", headers=headers, json={
            "action": "enable_cluster",
            "bind_address": "0.0.0.0",
            "username": "admin",
            "password": "password",
            "node_count": "3"
        })
        logging.info(f"[Cluster] enable_cluster: {res.status_code} - {res.text}")

        res = requests.post(f"{base_url}/_cluster_setup", headers=headers, json={
            "action": "add_node",
            "host": "couchdb2.local",
            "port": 5984,
            "username": "admin",
            "password": "password"
        })
        logging.info(f"[Cluster] add_node couchdb2: {res.status_code} - {res.text}")

        res = requests.post(f"{base_url}/_cluster_setup", headers=headers, json={
            "action": "add_node",
            "host": "couchdb3.local",
            "port": 5984,
            "username": "admin",
            "password": "password"
        })
        logging.info(f"[Cluster] add_node couchdb3: {res.status_code} - {res.text}")

        res = requests.post(f"{base_url}/_cluster_setup", headers=headers, json={
            "action": "finish_cluster"
        })
        logging.info(f"[Cluster] finish_cluster: {res.status_code} - {res.text}")

    except Exception as e:
        logging.error(f"⛔ Erreur lors de la création du cluster CouchDB : {e}")
        raise


def wait_for_cluster_ready():
    base_url = f"{COUCHDB_URL}/_membership"
    for i in range(20):
        try:
            res = requests.get(base_url)
            if res.status_code == 200:
                nodes = res.json().get("all_nodes", [])
                if len(nodes) >= 3:
                    logging.info(f"✅ Cluster prêt avec nœuds : {nodes}")
                    return
        except Exception as e:
            logging.warning(f"[Cluster] Attente cluster ({i}) : {e}")
        time.sleep(3)
    raise RuntimeError("❌ Cluster CouchDB non prêt après 60s")



# === GRAHAM SCAN ===
def grahamScan(geojson_list):
    points = [feature["coordinates"] for feature in geojson_list if feature["type"] == "Point"]
    if len(points) < 3:
        return None
    hull = ConvexHull(points)
    hull_points = [points[i] for i in hull.vertices]
    hull_points.append(hull_points[0])
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [hull_points]},
        "properties": {}
    }


# === TRANSFORMATIONS ===
def transformToJSON(df):
    trees = {}
    for _, row in df.iterrows():
        tree_id = row["idTree"]
        if tree_id not in trees:
            trees[tree_id] = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]},
                "properties": {
                    "forest": row["Forest"],
                    "plot": {
                        "id": row["Plot"],
                        "area": row["PlotArea"],
                        "sub_plot": {"id": row["SubPlot"]}
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
        convex = grahamScan(row["geometry"])
        for tree in trees.values():
            if tree["properties"]["plot"]["id"] == row["Plot"]:
                tree["properties"]["plot"]["location"] = convex

    for _, row in grouped_sub_geometry.iterrows():
        convex = grahamScan(row["geometry"])
        for tree in trees.values():
            if (tree["properties"]["plot"]["id"] == row["Plot"] and
                tree["properties"]["plot"]["sub_plot"]["id"] == row["SubPlot"]):
                tree["properties"]["plot"]["sub_plot"]["location"] = convex

    return trees


def transformToJSON2(df):
    plots = {}
    grouped = df.groupby("Plot")

    grouped_geometry = df.groupby("Plot").apply(lambda g: [
        {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
    ]).reset_index(name="geometry")

    grouped_sub_geometry = df.groupby(["Plot", "SubPlot"]).apply(lambda g: [
        {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
    ]).reset_index(name="geometry")

    for plot_id, group in grouped:
        geo_group = grouped_geometry[grouped_geometry["Plot"] == plot_id]
        convex = grahamScan(geo_group["geometry"].iloc[0])

        plots[plot_id] = {
            "type": "Feature",
            "geometry": convex["geometry"],
            "properties": {
                "plot": {"id": plot_id, "area": group["PlotArea"].iloc[0]},
                "sub_plots": {"type": "FeatureCollection", "features": []},
                "trees": {"type": "FeatureCollection", "features": []}
            }
        }

        sub_plots_set = set()
        trees_set = set()

        for _, row in group.iterrows():
            sub_plot_id = row["SubPlot"]
            if sub_plot_id not in sub_plots_set:
                sub_plots_set.add(sub_plot_id)
                geo_sub = grouped_sub_geometry[
                    (grouped_sub_geometry["Plot"] == plot_id) &
                    (grouped_sub_geometry["SubPlot"] == sub_plot_id)
                ]
                convex_sub = grahamScan(geo_sub["geometry"].iloc[0])
                plots[plot_id]["properties"]["sub_plots"]["features"].append({
                    "type": "Feature",
                    "geometry": convex_sub["geometry"],
                    "properties": {"id": sub_plot_id}
                })

            tree_id = row["idTree"]
            if tree_id not in trees_set:
                trees_set.add(tree_id)
                species = {
                    "source": row["BotaSource"],
                    "certainty": row["BotaCertainty"] == "VRAI"
                }
                for key in ["Family", "Genus", "Species"]:
                    if "Indet." not in row[key]:
                        species[key.lower()] = row[key]

                plots[plot_id]["properties"]["trees"]["features"].append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]},
                    "properties": {
                        "tree_id": tree_id,
                        "field_number": row["TreeFieldNum"],
                        "sub_plot_id": sub_plot_id,
                        "species": species,
                        "vernacular": {
                            "id": row["idVern"],
                            "name": row["VernName"],
                            "commercial_species": row["CommercialSp"] == "VRAI"
                        },
                        "measurements": []
                    }
                })

            # Ajout des mesures
            for tree in plots[plot_id]["properties"]["trees"]["features"]:
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


def transformToJSON3(df):
    plots = {}
    grouped_data = df.groupby("Plot")

    grouped_geometry = df.groupby("Plot").apply(lambda g: [
        {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
    ]).reset_index(name="geometry")

    grouped_sub_geometry = df.groupby(["Plot", "SubPlot"]).apply(lambda g: [
        {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]} for _, row in g.iterrows()
    ]).reset_index(name="geometry")

    for plot_id, group in grouped_data:
        geo_group = grouped_geometry[grouped_geometry["Plot"] == plot_id]
        convex = grahamScan(geo_group["geometry"].iloc[0])

        plots[plot_id] = {
            "type": "Feature",
            "geometry": convex["geometry"],
            "properties": {
                "plot": {"id": plot_id, "area": group["PlotArea"].iloc[0]},
                "sub_plots": {"type": "FeatureCollection", "features": []},
                "trees": {"type": "FeatureCollection", "features": []}
            }
        }

        sub_plots_set = set()
        for _, row in group.iterrows():
            sub_plot_id = row["SubPlot"]
            if sub_plot_id not in sub_plots_set:
                sub_plots_set.add(sub_plot_id)
                geo_sub = grouped_sub_geometry[
                    (grouped_sub_geometry["Plot"] == plot_id) &
                    (grouped_sub_geometry["SubPlot"] == sub_plot_id)
                ]
                convex_sub = grahamScan(geo_sub["geometry"].iloc[0])
                plots[plot_id]["properties"]["sub_plots"]["features"].append({
                    "type": "Feature",
                    "geometry": convex_sub["geometry"],
                    "properties": {"id": sub_plot_id}
                })

            tree = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row["Lon"], row["Lat"]]},
                "properties": {
                    "tree_field_number": row["TreeFieldNum"],
                    "tree_id": row["idTree"],
                    "sub_plot_id": sub_plot_id,
                    "tree_species_family": row["Family"] if "Indet." not in row["Family"] else "",
                    "tree_species_genus": row["Genus"] if "Indet." not in row["Genus"] else "",
                    "tree_species_species": row["Species"] if "Indet." not in row["Species"] else "",
                    "tree_species_source": row["BotaSource"],
                    "tree_species_certainty": row["BotaCertainty"] == "VRAI",
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
            }

            plots[plot_id]["properties"]["trees"]["features"].append(tree)

    return plots


# === INIT + INSERTION ===
def create_db_if_not_exists(db_name):
    res = requests.put(f"{COUCHDB_URL}/{db_name}")
    if res.status_code not in (201, 412):
        logging.error(f"[ERREUR] Création base {db_name}: {res.status_code} - {res.text}")
        raise RuntimeError("Échec création BDD")


def insert_bulk(db_name, docs):
    if not docs:
        logging.warning(f"[WARN] Aucun document pour {db_name}")
        return
    res = requests.post(f"{COUCHDB_URL}/{db_name}/_bulk_docs", headers=HEADERS, data=json.dumps({"docs": docs}))
    if res.status_code == 201:
        logging.info(f"[OK] {len(docs)} documents insérés dans {db_name}")
    else:
        logging.error(f"[ERREUR] Insertion dans {db_name} : {res.status_code} - {res.text}")


def insertData():
    dbs = {
        "forest1": transformToJSON,
        "forest2": transformToJSON2,
        "forest3": transformToJSON3
    }

    for db in dbs:
        create_db_if_not_exists(db)

    csv_files = glob.glob("./DataForest/*.csv")
    logging.info(f"CSV détectés : {csv_files}")

    data_type = {2: float, 6: float, 7: float, 27: str}

    for file in csv_files:
        df = pd.read_csv(file, dtype=data_type, decimal=',')
        for db_name, transformer in dbs.items():
            try:
                docs_dict = transformer(df)
                insert_bulk(db_name, list(docs_dict.values()))
            except Exception as e:
                logging.error(f"[ERREUR] pour {db_name} → {e}")

    logging.info("✅ Initialisation CouchDB terminée.")


def extract_ids(dbname, output_file, user=None, password=None):
    url = "http://couchdb1:5984"
    couchdb_url = url.rstrip('/') + f'/{dbname}/_all_docs'
    params = {"include_docs": "false"}
    auth = (user, password) if user and password else None

    response = requests.get(couchdb_url, params=params, auth=auth)
    response.raise_for_status()

    data = response.json()
    rows = data.get("rows", [])

    with open(output_file, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(str(row["id"]) + "\n")

    print(f"✅ {len(rows)} _id écrits dans {output_file}")

# Lancement
init_cluster()
wait_for_cluster_ready()
insertData()
extract_ids("forest1", "/app/output/forest1_ids.txt",  "admin", "password")
extract_ids("forest2", "/app/output/forest2_ids.txt",  "admin", "password")
extract_ids("forest3", "/app/output/forest3_ids.txt",  "admin", "password")

