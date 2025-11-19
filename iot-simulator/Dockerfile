FROM python:3.11-slim

# Disable Python output buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator code
COPY iot_simulator.py .

# Default command
CMD ["python", "-u", "iot_simulator.py", "--kafka-server", "kafka:29092", "--kafka-topic", "wastewater-sensors", "--daily-pattern", "--interval", "1"]
