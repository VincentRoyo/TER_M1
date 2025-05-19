from locust import User, task, between, events
from pymongo import MongoClient
import time
import bson
import csv
import os
from collections import defaultdict

from Mongo.Workloads import forest1, forest2, forest3

# Accumulateur pour métriques personnalisées
custom_metrics = defaultdict(lambda: {"bytes": 0, "docs": 0, "calls": 0})


class MongoUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        self.client = MongoClient("mongodb://admin:password@mongodb:27017/")
        db = self.client["TER"]

        self.workloads = {
            "forest1": forest1.get_queries(db["forest1"]),
            "forest2": forest2.get_queries(db["forest2"]),
            "forest3": forest3.get_queries(db["forest3"]),
        }

    @task
    def run_workload(self):
        for collection_name, queries in self.workloads.items():
            for query_name, query_func in queries.items():
                start = time.time()
                try:
                    result = list(query_func())
                    duration = (time.time() - start) * 1000

                    doc_count = len(result)
                    total_bytes = sum(len(bson.BSON.encode(doc)) for doc in result)

                    key = (collection_name, query_name)
                    custom_metrics[key]["docs"] += doc_count
                    custom_metrics[key]["bytes"] += total_bytes
                    custom_metrics[key]["calls"] += 1

                    events.request.fire(
                        request_type="MONGO",
                        name=f"[{collection_name}] {query_name}",
                        response_time=duration,
                        response_length=total_bytes,
                        exception=None
                    )
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    events.request.fire(
                        request_type="MONGO",
                        name=f"[{collection_name}] {query_name}",
                        response_time=duration,
                        response_length=0,
                        exception=e
                    )


def extract_key(locust_name):
    """
    Extrait (collection, requête) depuis le nom Locust : "[forest1] query" → ("forest1", "query")
    """
    try:
        bracket_part, rest = locust_name.split("]", 1)
        collection = bracket_part.strip("[")
        query_name = rest.strip()
        return (collection, query_name)
    except Exception:
        return ("unknown", locust_name)


@events.test_stop.add_listener
def export_mongodb_metrics_csv(environment, **kwargs):
    output_path = "/app/output/locust_metrics.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Request Name", "Request Type", "Num Requests", "Num Failures",
            "Median Response Time (ms)", "Average Response Time (ms)",
            "Min Response Time (ms)", "Max Response Time (ms)",
            "Total Bytes", "Avg Bytes/Request",
            "Custom Doc Count", "Avg Docs/Request"
        ])

        for (request_name, request_type), stats in environment.stats.entries.items():
            if request_type != "MONGO":
                continue

            total_bytes = stats.total_content_length
            num_requests = stats.num_requests
            num_failures = stats.num_failures
            avg_bytes = total_bytes / num_requests if num_requests else 0

            # Récupération des métriques personnalisées
            custom = custom_metrics.get(extract_key(request_name), {})
            total_docs = custom.get("docs", 0)
            avg_docs = total_docs / custom.get("calls", 1) if custom.get("calls", 1) else 0

            writer.writerow([
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
                round(avg_docs, 2)
            ])

    print(f"[INFO] Rapport exporté dans : {output_path}")

