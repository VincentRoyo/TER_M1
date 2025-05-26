from locust import User, task, between, events
from pymongo import MongoClient
import time
import bson
import csv
import os
from collections import defaultdict
import threading
from locust.exception import StopUser
import requests

from Mongo.Workloads import forest1, forest2, forest3

MONGO_CONTAINER_NAME = "mongodb_container"
CADVISOR_HOST = "http://cadvisor:8080"

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

def get_container_stats(container_name):
    try:
        response = requests.get(f"{CADVISOR_HOST}/api/v1.3/subcontainers")
        containers = response.json()
        for container in containers:
            if container_name in container.get("aliases", []):
                stats = container.get("stats", [])
                if not stats:
                    return 0, 0
                last = stats[-1]
                cpu = last["cpu"].get("usage", {}).get("total", 0)
                mem = last["memory"].get("working_set", 0)
                return cpu, mem
    except Exception as e:
        print(f"[WARN] Stat collection failed: {e}")
    return 0, 0

class MongoUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        self.client = MongoClient("mongodb://admin:password@mongodb:27017/")
        db = self.client["TER"]

        self.query_limit = self.environment.parsed_options.query_count or 0
        self.query_counts = defaultdict(int)
        self.lock = threading.Lock()

        self.workloads = {
            "forest1": forest1.get_queries(db["forest1"]),
            "forest2": forest2.get_queries(db["forest2"]),
            "forest3": forest3.get_queries(db["forest3"]),
        }

    @task
    def run_workload(self):
        with self.lock:
            expected_total = len(self.workloads) * max(len(q) for q in self.workloads.values())
            if len(self.query_counts) == expected_total and all(v >= self.query_limit for v in self.query_counts.values()):
                raise StopUser()

        for collection_name, queries in self.workloads.items():
            for query_name, query_func in queries.items():
                key = (collection_name, query_name)

                with self.lock:
                    if self.query_counts[key] >= self.query_limit:
                        continue
                    self.query_counts[key] += 1

                cpu_before, mem_before = get_container_stats(MONGO_CONTAINER_NAME)
                start = time.time()

                try:
                    result = list(query_func())
                    duration = (time.time() - start) * 1000
                    cpu_after, mem_after = get_container_stats(MONGO_CONTAINER_NAME)

                    doc_count = len(result)
                    total_bytes = sum(len(bson.BSON.encode(doc)) for doc in result)

                    custom_metrics[key]["docs"] += doc_count
                    custom_metrics[key]["bytes"] += total_bytes
                    custom_metrics[key]["calls"] += 1
                    custom_metrics[key]["latencies"].append(duration)
                    custom_metrics[key]["min"] = min(custom_metrics[key]["min"], duration)
                    custom_metrics[key]["max"] = max(custom_metrics[key]["max"], duration)
                    custom_metrics[key]["cpu"].append(cpu_after - cpu_before)
                    custom_metrics[key]["mem"].append(mem_after)

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
    try:
        bracket_part, rest = locust_name.split("]", 1)
        collection = bracket_part.strip("[")
        query_name = rest.strip()
        return (collection, query_name)
    except Exception:
        return ("unknown", locust_name)

@events.test_stop.add_listener
def export_mongodb_metrics_csv(environment, **kwargs):
    output_path = "/app/output/locust_metrics_mongo.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    grouped = {
        "forest1": [],
        "forest2": [],
        "forest3": [],
        "unknown": []
    }

    for (request_name, request_type), stats in environment.stats.entries.items():
        if request_type != "MONGO":
            continue

        collection, query_name = extract_key(request_name)
        total_bytes = stats.total_content_length
        num_requests = stats.num_requests
        num_failures = stats.num_failures
        avg_bytes = total_bytes / num_requests if num_requests else 0

        custom = custom_metrics.get((collection, query_name), {})
        total_docs = custom.get("docs", 0)
        avg_docs = total_docs / custom.get("calls", 1) if custom.get("calls", 1) else 0
        min_latency = round(custom.get("min", 0), 2)
        max_latency = round(custom.get("max", 0), 2)
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
            min_latency,
            max_latency,
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

