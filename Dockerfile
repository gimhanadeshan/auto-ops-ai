# Multi-stage Docker build for Auto-Ops-AI Backend
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/processed /app/data/raw /app/logs && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (includes ML models in backend/app/models/ml/)
COPY --chown=appuser:appuser backend/app /app/app

# Copy initialization and ingestion scripts
COPY --chown=appuser:appuser backend/init_db.py /app/init_db.py
COPY --chown=appuser:appuser backend/check_config.py /app/check_config.py
COPY --chown=appuser:appuser backend/ingestion_script.py /app/ingestion_script.py
COPY --chown=appuser:appuser backend/migrations.py /app/migrations.py
COPY --chown=appuser:appuser backend/migrate_add_assignment.py /app/migrate_add_assignment.py
COPY --chown=appuser:appuser backend/update_categories.py /app/update_categories.py

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
