# syntax=docker/dockerfile:1

FROM python:3.9.6-slim-bullseye

WORKDIR /app

COPY requirements.txt .
COPY httpc.py .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "httpc.py"]