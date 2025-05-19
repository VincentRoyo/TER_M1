from locust import HttpUser, task, between
import random
import os
import csv

# Préparation des données : on lit tous les idPlot et idSubPlot du CSV
plot_ids = set()
subplot_ids = set()

plot_ids = set()
subplot_ids = set()

csv_path = "/locust/forest.csv"

# 1. Vérifie que le fichier existe
if not os.path.exists(csv_path):
    print(f"[ERREUR] Le fichier CSV est introuvable à l'emplacement : {csv_path}")
else:
    print(f"[OK] Fichier CSV trouvé à : {csv_path}")

    # 2. Affiche les 3 premières lignes du fichier brut
    print("[INFO] Aperçu du contenu brut du fichier CSV :")
    with open(csv_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            print(line.strip())
            if i >= 2:
                break  # ne lire que les 3 premières lignes


with open(csv_path, newline='', encoding='utf-8') as csvfile:

    reader = csv.DictReader(csvfile, delimiter=',')
    
    print(f"[DEBUG] Noms de colonnes détectés : {reader.fieldnames}")
    
    for row in reader:
        plot = row.get("Plot")
        subplot = row.get("SubPlot")

        if plot:
            plot_ids.add(str(plot).strip())

        if subplot:
            try:
                subplot_ids.add(int(str(subplot).strip()))
            except ValueError:
                continue


# Transforme les ensembles en listes triées pour avoir une itération stable
plot_ids = sorted(list(plot_ids))
subplot_ids = sorted(list(subplot_ids))

# Toutes les combinaisons possibles plot/subplot
plot_subplot_combinations = [(p, s) for p in plot_ids for s in subplot_ids]

class ApiUser(HttpUser):
    # Attente entre les requêtes : de 1 à 3 secondes
    wait_time = between(1, 3)

    @task(2)
    def get_all(self):
        self.client.get("/all", name="/all")

    @task(2)
    def get_all_geo(self):
        self.client.get("/allgeo", name="/allgeo")

    @task(2)
    def get_geoplot(self):
        self.client.get("/geoplot", name="/geoplot")

    @task(3)
    def get_plot_info(self):
        plot = random.choice(plot_ids)
        self.client.get(f"/infoplot/{plot}", name="/infoplot/:idPlot")

    @task(3)
    def get_plot_subplot_info(self):
        plot, subplot = random.choice(plot_subplot_combinations)
        self.client.get(f"/infoplot/{plot}/{subplot}", name="/infoplot/:idPlot/:idSubPlot")

