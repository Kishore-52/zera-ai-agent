FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Required for generating the Energy Hazard Graph
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create runtime folders and seed the prototype safety memory
RUN mkdir -p storage/qdrant storage/audit \
    && python scripts/seed_qdrant.py

EXPOSE 10000

CMD ["sh", "-c", "gunicorn flask_app:app --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120"]