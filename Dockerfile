FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ARM 64 compatibility ----------
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    python3-dev \
    cmake \
    libgmp-dev \
    libreadline-dev \
    libncurses-dev \
    zlib1g-dev \
    libbz2-dev \
    libboost-dev \
    libtbb-dev \
    && wget https://scipopt.org/download/release/scipoptsuite-9.2.4.tgz \
    && tar xzf scipoptsuite-9.2.4.tgz \
    && cd scipoptsuite-9.2.4 \
    && mkdir build && cd build \
    && cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local -DIPOPT=off \
    && make -j$(nproc) \
    && make install \
    && cd ../.. \
    && rm -rf scipoptsuite-9.2.4*
# -------------------------------

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

# Remove build tools to slim image after wheels are built
RUN apt-get remove --purge -y wget cmake build-essential python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
COPY api/ .
COPY eriemodel/ ./eriemodel/

# Switch to non-privileged user
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
