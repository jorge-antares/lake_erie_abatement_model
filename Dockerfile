ARG PYTHON_VERSION=3.13.0
FROM python:${PYTHON_VERSION}-slim AS base

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


RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=api/requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY api/ .
COPY eriemodel/ ./eriemodel/

# Create logs directory and set permissions
RUN mkdir -p api/logs && chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
