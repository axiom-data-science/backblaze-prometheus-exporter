# Backblaze Prometheus Exporter

Export prometheus metrics on last update time and size of paths in Backblaze B2 storage.

## Usage

A Backblaze B2 API key with read access to the desired buckets is required.

### Run

Install python dependencies using pip (`pip install -r requirements.txt`).
Use of a virtual python environment is advised.

Configuration via environment variables:

* Set `B2_APPLICATION_KEY_ID` to the key ID.
* Set `B2_APPLICATION_KEY_FILE` to a file containing the B2 api key, or set `B2_APPLICATION_KEY` to the key directly (insecure).
* Set `B2_PATHS` to a json representation of a dictionary. Keys are buckets, values are lists of paths in that bucket to monitor.
  Example: '{"my-bucket": ["some/path/to/check", "some/other/path/to/check"]}'

Optionally:

* Set `METRICS_PORT` to the port to be used. Default is 52000.
* Set `UPDATE_INTERVAL` to the interval between updates, in seconds. Default is 30 minutes.

Finally:

```bash
python ./backblaze-prometheus-exporter.py
```

Or, setting the environment variables on the command line when executing:

```bash
B2_APPLICATION_KEY_ID=keyid B2_APPLICATION_KEY_FILE=./api_key \
B2_PATHS='{"my-bucket": ["some/path/to/check", "some/other/path/to/check"]}' \
./backblaze-prometheus-exporter.py
```

### Run with Docker

Build the Docker image:

```bash
docker build -t backblaze-prometheus-exporter .
```

Then run:

```bash
docker run --rm -p 52000:52000 -v $(pwd)/b2_api_key:/etc/b2/api_key:ro \
  -e B2_APPLICATION_KEY_ID=yourkeyid \
  -e B2_APPLICATION_KEY_FILE=/etc/b2/api_key \
  -e B2_PATHS='{"my-bucket": ["some/path/to/check", "some/other/path/to/check"]}' \
  --name backblaze-prometheus-exporter \
  backblaze-prometheus-exporter
```
