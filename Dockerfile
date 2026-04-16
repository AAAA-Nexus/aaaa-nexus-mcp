# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "aaaa_nexus_mcp"]
