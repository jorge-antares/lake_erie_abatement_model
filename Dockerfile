# ── Stage 1: build SCIP from source and install Python packages ──────────
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    python3-dev \
    cmake \
    libgmp-dev \
    libreadline-dev \
    libncurses-dev \
    zlib1g-dev \
    libbz2-dev \
    libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

# ARM 64 compatibility ----------
RUN wget -q https://scipopt.org/download/release/scipoptsuite-9.2.4.tgz \
    && tar xzf scipoptsuite-9.2.4.tgz \
    && cd scipoptsuite-9.2.4 \
    && mkdir build && cd build \
    && cmake .. \
          -DCMAKE_INSTALL_PREFIX=/usr/local \
          -DIPOPT=off \
          -DPAPILO=off \
          -DCMAKE_BUILD_TYPE=Release \
    && make -j$(nproc) \
    && make install \
    && cd ../.. \
    && rm -rf scipoptsuite-9.2.4* \
    && find /usr/local/lib -name "*.a" -delete
# -------------------------------

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=api/requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# ── Stage 2: lean runtime image ──────────────────────────────────────────
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

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

# Runtime libraries required by SCIP
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgmp10 \
    libreadline8 \
    libncurses6 \
    zlib1g \
    libbz2-1.0 \
    libtbb12 \
    && rm -rf /var/lib/apt/lists/*

# Copy SCIP shared libraries and installed Python packages from builder
COPY --from=builder /usr/local/lib/ /usr/local/lib/
RUN ldconfig

COPY api/ .
COPY eriemodel/ ./eriemodel/

# Switch to non-privileged user
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=120s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
