FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e ".[parquet]"

RUN useradd --create-home --uid 10001 drift \
    && chown -R drift:drift /app
USER drift

CMD ["python", "-m", "driftlab.cli", "--help"]

