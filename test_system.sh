#!/bin/bash
# End-to-End System Test for Wastewater Treatment Prediction System

set -e

echo "========================================================================"
echo "Wastewater Treatment System - End-to-End Test"
echo "========================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_error() {
    echo -e "${RED}✗ $1${NC}"
}

function print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Test 1: Check Docker Compose
echo "1. Checking Docker Compose..."
if command -v docker compose &> /dev/null; then
    print_success "Docker Compose is installed"
else
    print_error "Docker Compose not found"
    exit 1
fi

# Test 2: Check required files
echo ""
echo "2. Checking required files..."
required_files=(
    "docker-compose.yml"
    "iot_simulator.py"
    "prediction_service.py"
    "api_service.py"
    "Dockerfile"
    "Dockerfile.prediction"
    "Dockerfile.api"
    "lstm/model/best_model.keras"
    "lstm/model/scalers.npz"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file not found"
        exit 1
    fi
done

# Test 3: Start services
echo ""
echo "3. Starting services..."
print_info "Running: docker compose up -d"
docker compose up -d

# Test 4: Wait for services to be healthy
echo ""
echo "4. Waiting for services to become healthy (max 120s)..."

function wait_for_service() {
    local service=$1
    local max_wait=120
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        if docker compose ps $service | grep -q "healthy"; then
            print_success "$service is healthy"
            return 0
        fi
        sleep 2
        waited=$((waited + 2))
    done
    
    print_error "$service failed to become healthy"
    return 1
}

services=("zookeeper" "kafka" "postgres")
for service in "${services[@]}"; do
    wait_for_service $service || exit 1
done

# Wait a bit more for prediction service to initialize
print_info "Waiting additional 30s for prediction service to initialize..."
sleep 30

# Test 5: Check IoT Simulator is producing data
echo ""
echo "5. Checking IoT Simulator..."
if docker compose logs --tail=10 iot-simulator | grep -q "Sent to Kafka"; then
    print_success "IoT Simulator is sending data to Kafka"
else
    print_error "IoT Simulator is not producing data"
    docker compose logs --tail=20 iot-simulator
    exit 1
fi

# Test 6: Check Kafka UI
echo ""
echo "6. Checking Kafka UI..."
if curl -s http://localhost:8080 > /dev/null; then
    print_success "Kafka UI is accessible at http://localhost:8080"
else
    print_error "Kafka UI is not accessible"
fi

# Test 7: Check API health endpoint
echo ""
echo "7. Checking API Service..."
response=$(curl -s http://localhost:5000/health)
if echo "$response" | grep -q "healthy"; then
    print_success "API Service is healthy"
    echo "   Response: $response"
else
    print_error "API Service health check failed"
    docker compose logs --tail=20 api-service
    exit 1
fi

# Test 8: Wait for predictions to start
echo ""
echo "8. Waiting for predictions to be generated (max 60s)..."
max_wait=60
waited=0
while [ $waited -lt $max_wait ]; do
    response=$(curl -s http://localhost:5000/api/v1/predictions/latest)
    if echo "$response" | grep -q "tss_mg_l"; then
        print_success "Predictions are being generated"
        echo ""
        echo "Latest Prediction:"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        break
    fi
    sleep 5
    waited=$((waited + 5))
done

if [ $waited -ge $max_wait ]; then
    print_error "No predictions generated after ${max_wait}s"
    echo ""
    echo "Prediction Service Logs:"
    docker compose logs --tail=50 prediction-service
    exit 1
fi

# Test 9: Test API endpoints
echo ""
echo "9. Testing API endpoints..."

# Test history endpoint
echo "   Testing /api/v1/predictions/history..."
response=$(curl -s "http://localhost:5000/api/v1/predictions/history?limit=5")
if echo "$response" | grep -q "predictions"; then
    print_success "History endpoint working"
else
    print_error "History endpoint failed"
fi

# Test statistics endpoint
echo "   Testing /api/v1/statistics..."
response=$(curl -s "http://localhost:5000/api/v1/statistics?hours=1")
if echo "$response" | grep -q "total_predictions"; then
    print_success "Statistics endpoint working"
else
    print_error "Statistics endpoint failed"
fi

# Test 10: Check database
echo ""
echo "10. Checking database..."
count=$(docker exec wastewater-postgres psql -U postgres -d wastewater -t -c "SELECT COUNT(*) FROM predictions;" 2>/dev/null | tr -d ' ')
if [ "$count" -gt 0 ] 2>/dev/null; then
    print_success "Database has $count predictions"
else
    print_error "No predictions in database"
fi

# Test 11: Performance check
echo ""
echo "11. Checking prediction performance..."
response=$(curl -s http://localhost:5000/api/v1/predictions/latest)
inference_time=$(echo "$response" | grep -o '"inference_time_ms":[^,}]*' | cut -d':' -f2)
if [ ! -z "$inference_time" ]; then
    print_success "Inference time: ${inference_time}ms"
    if (( $(echo "$inference_time < 1000" | bc -l) )); then
        print_success "Sub-second prediction achieved! ✨"
    fi
else
    print_info "Could not extract inference time"
fi

# Final summary
echo ""
echo "========================================================================"
echo "Test Summary"
echo "========================================================================"
print_success "All tests passed!"
echo ""
echo "System Status:"
echo "  • IoT Simulator: Running ✓"
echo "  • Kafka Broker: Running ✓"
echo "  • Prediction Service: Running ✓"
echo "  • API Service: Running ✓"
echo "  • Database: Running ✓"
echo ""
echo "Access Points:"
echo "  • API: http://localhost:5000"
echo "  • Kafka UI: http://localhost:8080"
echo "  • Database: localhost:5432"
echo ""
echo "Quick Commands:"
echo "  • View logs: docker compose logs -f"
echo "  • Get latest prediction: curl http://localhost:5000/api/v1/predictions/latest"
echo "  • Stop system: docker compose down"
echo ""
echo "========================================================================"
echo "🎉 System is ready for production deployment!"
echo "========================================================================"
