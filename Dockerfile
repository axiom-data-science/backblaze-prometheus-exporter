FROM python:3.13-alpine

WORKDIR /b2prom

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY backblaze-prometheus-exporter.py ./

USER guest

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["./backblaze-prometheus-exporter.py"]
