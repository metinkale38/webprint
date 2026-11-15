# syntax=docker/dockerfile:1.7

FROM node:22-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM ubuntu:24.04 AS runtime
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Berlin \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    cups cups-daemon cups-client cups-filters \
    printer-driver-all hplip printer-driver-gutenprint foomatic-db printer-driver-cups-pdf \
    snmp python3 python3-venv python3-pip \
    curl ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/cups-defaults && cp -a /etc/cups/. /opt/cups-defaults/

WORKDIR /app/backend
COPY backend/requirements.txt /app/backend/requirements.txt
RUN python3 -m venv /app/.venv \
    && /app/.venv/bin/pip install --no-cache-dir --upgrade pip \
    && /app/.venv/bin/pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY --from=frontend /app/frontend/dist /app/backend/static
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && mkdir -p /app/data /app/uploads /var/spool/cups /var/log/cups

EXPOSE 631 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
