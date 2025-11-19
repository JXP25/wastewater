#!/bin/bash
# Complete setup script for Wastewater IoT Simulation with Kafka

set -e

echo "========================================"
echo "Wastewater IoT Kafka Setup"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed (v2 format)
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker with Compose plugin."
    exit 1
fi

echo "✓ Docker and Docker Compose found"
echo ""

# Build IoT simulator image
echo "🔨 Building IoT simulator Docker image..."
docker compose build iot-simulator

echo ""
echo "🚀 Starting all services (Kafka + IoT Simulator)..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if Kafka is healthy
if docker ps | grep -q "wastewater-kafka"; then
    echo "✓ Kafka is running"
else
    echo "❌ Kafka failed to start"
    docker-compose logs kafka
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Services running:"
echo "  - Kafka: localhost:9092"
echo "  - Kafka UI: http://localhost:8080"
echo "  - Zookeeper: localhost:2181"
echo "  - IoT Simulator: Streaming to Kafka"
echo ""
echo "View real-time data:"
echo "  • Kafka UI: http://localhost:8080"
echo "  • View logs: docker compose logs -f iot-simulator"
echo "  • Consumer script: ./consume_kafka.sh"
echo ""
echo "Manage services:"
echo "  • View all logs: docker compose logs -f"
echo "  • Stop simulator: docker compose stop iot-simulator"
echo "  • Restart simulator: docker compose restart iot-simulator"
echo "  • Stop all: docker compose down"
echo ""
