FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install SCIP and build dependencies for ARM compatibility ---------
RUN apt-get update && apt-get install -y \
    build-essential \
    zlib1g-dev \
    libreadline-dev \
    libxml2-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the downloaded SCIP Debian package into the container
COPY SCIPOptSuite-*.deb /tmp/scip_install.deb

# Install the SCIP suite using dpkg and remove the installer file
RUN dpkg -i /tmp/scip_install.deb \
    && rm /tmp/scip_install.deb
# ------------------------------------------------------------------

# Non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Installation
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=api/requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY api/ .
COPY eriemodel/ ./eriemodel/

# Switch to non-privileged user
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
