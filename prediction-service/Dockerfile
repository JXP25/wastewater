FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY prediction_service.py .

# Disable Python output buffering for real-time logs
ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "prediction_service.py"]
