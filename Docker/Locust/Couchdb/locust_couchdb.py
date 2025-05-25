from locust import User, task, between, events
import requests
import time
import json
import csv
import os
from collections import defaultdict
import threading
from locust.exception import StopUser
from Couchdb.Workloads import forest1, forest2, forest3

COUCHDB_URL = "http://admin:password@couchdb1:5984"
CADVISOR_HOST = "http://cadvisor:8080"
CADVISOR_CONTAINER = "couchdb1"

custom_metrics = defaultdict(lambda: {
    "bytes": 0,
    "docs": 0,
    "calls": 0,
    "latencies": [],
    "min": float("inf"),
    "max": float("-inf"),
    "cpu": [],
    "mem": []
})

class CouchdbUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        self.session = requests.Session()
        self.session.auth = ("admin", "password")

        self.query_limit = self.environment.parsed_options.query_count or 0
        self.query_counts = defaultdict(int)
        self.lock = threading.Lock()

        forest1.create_views_forest(self.session, f"{COUCHDB_URL}/forest1")
        forest2.create_views_forest(self.session, f"{COUCHDB_URL}/forest2")
        forest3.create_views_forest(self.session, f"{COUCHDB_URL}/forest3")

        self.warmup_views("forest1", forest1.views_forest1)
        self.warmup_views("forest2", forest2.views_forest2)
        self.warmup_views("forest3", forest3.views_forest3)

        self.workloads = {
            "forest1": forest1.get_queries_forest(self.session, f"{COUCHDB_URL}/forest1"),
            "forest2": forest2.get_queries_forest(self.session, f"{COUCHDB_URL}/forest2"),
            "forest3": forest3.get_queries_forest(self.session, f"{COUCHDB_URL}/forest3"),
        }

    def warmup_views(self, db_name, views_dict, delay=2, timeout=60):
        print(f"[INFO] Warmup des vues pour {db_name}...")
        for view_name in views_dict.keys():
            url = f"{COUCHDB_URL}/{db_name}/_design/{db_name}/_view/{view_name}"
            start = time.time()
            while True:
                try:
                    r = self.session.get(url, params={"limit": 0})
                    if r.status_code == 200:
                        print(f"[OK] Vue {view_name} prête en {round((time.time() - start) * 1000)} ms")
                        break
                except Exception:
                    pass
                if time.time() - start > timeout:
                    print(f"[WARN] Timeout warmup pour vue {view_name}")
                    break
                time.sleep(delay)

    def get_container_metrics(self):
        try:
            r = requests.get(f"{CADVISOR_HOST}/api/v1.3/subcontainers")
            containers = r.json()
            for container in containers:
                aliases = container.get("aliases", [])
                if CADVISOR_CONTAINER in aliases:
                    stats = container.get("stats", [])
                    if not stats:
                        return None, None
                    latest = stats[-1]
                    cpu = latest["cpu"]["usage"]["total"]
                    mem = latest["memory"].get("working_set", latest["memory"].get("usage", 0))
                    return cpu, mem
            print(f"[WARN] Aucun conteneur trouvé avec l'alias '{CADVISOR_CONTAINER}' dans cAdvisor.")
        except Exception as e:
            print(f"[ERROR] Erreur lors de la récupération des métriques cAdvisor : {e}")
        return None, None

    @task
    def run_workload(self):
        with self.lock:
            expected_total = len(self.workloads) * max(len(q) for q in self.workloads.values())
            if len(self.query_counts) == expected_total and all(v >= self.query_limit for v in self.query_counts.values()):
                raise StopUser()

        for db_name, queries in self.workloads.items():
            for query_name, query_func in queries.items():
                key = (db_name, query_name)

                with self.lock:
                    if self.query_counts[key] >= self.query_limit:
                        continue
                    self.query_counts[key] += 1

                start = time.time()
                cpu_start, mem_start = self.get_container_metrics()

                try:
                    response = query_func()
                    duration = (time.time() - start) * 1000
                    cpu_end, mem_end = self.get_container_metrics()

                    if isinstance(response, requests.Response):
                        data = response.json()
                        content = response.content
                    else:
                        data = response
                        content = json.dumps(data).encode()

                    rows = data.get("rows", [])
                    doc_count = len(rows)
                    total_bytes = len(content)

                    custom_metrics[key]["docs"] += doc_count
                    custom_metrics[key]["bytes"] += total_bytes
                    custom_metrics[key]["calls"] += 1
                    custom_metrics[key]["latencies"].append(duration)
                    custom_metrics[key]["min"] = min(custom_metrics[key]["min"], duration)
                    custom_metrics[key]["max"] = max(custom_metrics[key]["max"], duration)

                    if cpu_start is not None and cpu_end is not None:
                        custom_metrics[key]["cpu"].append(cpu_end - cpu_start)
                    if mem_end is not None:
                        custom_metrics[key]["mem"].append(mem_end)

                    events.request.fire(
                        request_type="COUCHDB",
                        name=f"[{db_name}] {query_name}",
                        response_time=duration,
                        response_length=total_bytes,
                        exception=None
                    )
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    events.request.fire(
                        request_type="COUCHDB",
                        name=f"[{db_name}] {query_name}",
                        response_time=duration,
                        response_length=0,
                        exception=e
                    )

def extract_key(locust_name):
    try:
        bracket_part, rest = locust_name.split("]", 1)
        collection = bracket_part.strip("[")
        query_name = rest.strip()
        return (collection, query_name)
    except Exception:
        return ("unknown", locust_name)

@events.test_stop.add_listener
def export_couchdb_metrics_csv(environment, **kwargs):
    output_path = "/app/output/locust_metrics_couchdb.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    grouped = {
        "forest1": [],
        "forest2": [],
        "forest3": [],
        "unknown": []
    }

    for (request_name, request_type), stats in environment.stats.entries.items():
        if request_type != "COUCHDB":
            continue

        collection, query_name = extract_key(request_name)
        total_bytes = stats.total_content_length
        num_requests = stats.num_requests
        num_failures = stats.num_failures
        avg_bytes = total_bytes / num_requests if num_requests else 0

        custom = custom_metrics.get((collection, query_name), {})
        total_docs = custom.get("docs", 0)
        avg_docs = total_docs / custom.get("calls", 1) if custom.get("calls", 1) else 0
        min_latency = custom.get("min", 0)
        max_latency = custom.get("max", 0)
        avg_cpu = sum(custom.get("cpu", [])) / len(custom.get("cpu", [])) if custom.get("cpu") else 0
        avg_mem = sum(custom.get("mem", [])) / len(custom.get("mem", [])) if custom.get("mem") else 0

        grouped.get(collection, grouped["unknown"]).append([
            request_name,
            request_type,
            num_requests,
            num_failures,
            stats.median_response_time,
            stats.avg_response_time,
            stats.min_response_time,
            stats.max_response_time,
            total_bytes,
            round(avg_bytes, 2),
            total_docs,
            round(avg_docs, 2),
            round(min_latency, 2),
            round(max_latency, 2),
            round(avg_cpu, 2),
            round(avg_mem, 2)
        ])

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        headers = [
            "Request Name", "Request Type", "Num Requests", "Num Failures",
            "Median Response Time (ms)", "Average Response Time (ms)",
            "Min Response Time (ms)", "Max Response Time (ms)",
            "Total Bytes", "Avg Bytes/Request",
            "Custom Doc Count", "Avg Docs/Request",
            "Custom Min Latency", "Custom Max Latency",
            "Avg CPU Delta", "Avg Memory Working Set"
        ]

        for forest in ["forest1", "forest2", "forest3"]:
            writer.writerow([f"=== {forest.upper()} ==="])
            writer.writerow(headers)
            writer.writerows(grouped[forest])
            writer.writerow([])

    print(f"[INFO] Rapport exporté dans : {output_path}")

