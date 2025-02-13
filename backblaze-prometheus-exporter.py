#!/usr/bin/env python3
import json
import os
import prometheus_client as prom
import time

from b2sdk.v2 import B2Api, InMemoryAccountInfo

prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
prom.REGISTRY.unregister(prom.GC_COLLECTOR)

last_update = prom.Gauge("backblaze_b2_last_update_time",
                         "last update timestamp for a given bucket and path, in unix time.", ['bucket', 'path'])
total_size = prom.Gauge("backblaze_b2_total_size",
                        "total size of contents for a given bucket and path, in bytes.", ['bucket', 'path'])


def init_b2(application_key_id, application_key):
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", application_key_id, application_key)
    return b2_api


def get_path_stats(b2_api, bucket_name, path):
    bucket = b2_api.get_bucket_by_name(bucket_name)
    total_size = 0
    timestamps = []
    for file_version, folder_name in bucket.ls(latest_only=False, recursive=True, folder_to_list=path):
        total_size += file_version.size
        timestamps.append(file_version.upload_timestamp)

    latest_timestamp = max(timestamps)

    path_stats = {"path": path, "total_size": total_size,
                  "latest_timestamp": latest_timestamp}

    return path_stats


def update_path_gauges(b2_api, bucket_name, path):
    path_stats = get_path_stats(b2_api, bucket_name, path)
    last_update.labels(bucket=bucket_name, path=path).set(
        path_stats['latest_timestamp'])
    total_size.labels(bucket=bucket_name, path=path).set(
        path_stats['total_size'])


def update_gauges(b2_api, b2_pairs):
    for bucket, path in b2_pairs:
        update_path_gauges(b2_api, bucket, path)


def main():
    application_key_id = os.environ.get("B2_APPLICATION_KEY_ID", default=None)
    application_key_path = os.environ.get("B2_APPLICATION_KEY_FILE", default=None)
    if application_key_path is None:
        application_key = os.environ.get("B2_APPLICATION_KEY", default=None)
    else:
        with open(application_key_path, "r") as fp:
            application_key = fp.readline().strip()

    metrics_port = int(os.environ.get("METRICS_PORT", default="52000"))
    update_interval = int(os.environ.get(
        "UPDATE_INTERVAL", default=str(60*30)))
    b2_paths = os.environ.get("B2_PATHS", default=None)

    if application_key_id is None:
        print("Error: B2_APPLICATION_KEY_ID must be set")
        return 1
    if application_key is None and application_key_path is None:
        print("Error: One of B2_APPLICATION_KEY or B2_APPLICATION_KEY_FILE must be set")
        return 1
    if application_key_id is None:
        print("Error: B2_PATHS must be set.")
        print("Example contents:")
        print('{"my-bucket": ["some/path/to/check", "some/other/path/to/check"]}')
        return 1

    b2_paths_json = json.loads(b2_paths)

    b2_pairs = []
    for bucket in b2_paths_json:
        for path in b2_paths_json[bucket]:
            b2_pairs.append((bucket, path))

    b2_api = init_b2(application_key_id=application_key_id,
                     application_key=application_key)

    print(f"Starting metrics server on port {metrics_port}")
    prom.start_http_server(metrics_port)

    while True:
        update_gauges(b2_api=b2_api, b2_pairs=b2_pairs)
        print("updating.")
        time.sleep(update_interval)


if __name__ == "__main__":
    main()
