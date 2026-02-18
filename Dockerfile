# Base Image
FROM python:3.11-slim as builder

# Set env vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Final Stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m botuser
USER botuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Run
CMD ["python", "src/main.py"]
