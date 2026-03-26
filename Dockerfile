FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv pip install --system --no-cache .

# --- Runtime stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

# Create non-root user
RUN useradd --create-home oracle
USER oracle

# Project mount point (read-only)
VOLUME ["/project"]

ENV ORACLE_LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["mcp-codebase-oracle"]
