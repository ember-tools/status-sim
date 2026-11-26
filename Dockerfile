FROM nixos/nix:latest AS frontend

WORKDIR /build
RUN nix-channel --update
COPY shell.nix .
COPY frontend/package*.json frontend/
RUN cd frontend && nix-shell ../shell.nix --run "npm ci"
COPY frontend/ frontend/
ARG COMMIT=dev
ARG BUILD_TIME
ENV COMMIT=$COMMIT BUILD_TIME=$BUILD_TIME
RUN cd frontend && nix-shell ../shell.nix --run "npm run build"


FROM python:3.14-slim

LABEL org.opencontainers.image.title="Status Sim" \
      org.opencontainers.image.description="Radio and vehicle status exercises for fire brigades" \
      org.opencontainers.image.source="https://github.com/ember-tools/status-sim" \
      org.opencontainers.image.licenses="GPL-3.0"
WORKDIR /app
RUN groupadd -r statussim && useradd -r -g statussim statussim

ENV PIPENV_VENV_IN_PROJECT=1 \
    LOG_FORMAT=json
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv sync && pip uninstall -y pipenv

COPY src/ src/
COPY --from=frontend /build/frontend/dist src/frontend_dist

USER statussim
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
CMD ["/app/.venv/bin/uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
