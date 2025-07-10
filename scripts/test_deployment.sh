#!/bin/bash

# Test script for Recall deployment validation
# This script tests all deployment scenarios

echo "🧪 Testing Recall Deployment"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check if Docker is running
run_test "Docker Service" "docker info > /dev/null 2>&1"

# Test 2: Check if ports are available
run_test "Port 5000 Available" "! nc -z localhost 5000 2>/dev/null"

# Test 3: Build development Docker image
run_test "Build Development Image" "docker-compose -f docker-compose.web.yml build > /dev/null 2>&1"

# Test 4: Start development container
echo -e "\n${YELLOW}Starting development container...${NC}"
docker-compose -f docker-compose.web.yml up -d

# Wait for container to start
sleep 10

# Test 5: Check container health
run_test "Container Health Check" "docker ps --filter 'name=recall-web' --filter 'status=running' | grep -q recall-web"

# Test 6: Test API status endpoint
run_test "API Status Endpoint" "curl -f http://localhost:5000/api/status > /dev/null 2>&1"

# Test 7: Test main web page
run_test "Main Web Page" "curl -f http://localhost:5000 > /dev/null 2>&1"

# Test 8: Test file upload endpoint structure
run_test "Upload Endpoint Structure" "curl -X POST http://localhost:5000/api/upload 2>/dev/null | grep -q 'error'"

# Test 9: Check logs
run_test "Container Logs" "docker-compose -f docker-compose.web.yml logs --tail=10 2>/dev/null | grep -q 'recall'"

# Test 10: Test health check endpoint
run_test "Health Check Endpoint" "docker exec recall-web curl -f http://localhost:5000/api/status > /dev/null 2>&1"

# Cleanup development container
echo -e "\n${YELLOW}Cleaning up development container...${NC}"
docker-compose -f docker-compose.web.yml down

# Test 11: Check if SSL certificates can be generated
run_test "SSL Certificate Generation" "command -v openssl > /dev/null 2>&1"

# Test 12: Build production image
run_test "Build Production Image" "docker-compose -f docker-compose.production.yml build > /dev/null 2>&1"

# Test 13: Check nginx configuration
run_test "nginx Configuration" "docker run --rm -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t > /dev/null 2>&1"

# Test 14: Check if all required files exist
required_files=(
    "src/web/api.py"
    "src/web/templates/index.html"
    "requirements.txt"
    "docker-compose.web.yml"
    "docker-compose.production.yml"
    "Dockerfile.web"
    "Dockerfile.production"
    "run_web.py"
    "run_web_production.py"
    "nginx/nginx.conf"
)

for file in "${required_files[@]}"; do
    run_test "Required File: $file" "test -f $file"
done

# Test 15: Check Python dependencies
run_test "Python Dependencies" "pip install -r requirements.txt --dry-run > /dev/null 2>&1"

# Test 16: Check if gunicorn is available
run_test "Gunicorn Availability" "python -c 'import gunicorn' 2>/dev/null"

# Test 17: Check Flask app can be imported
run_test "Flask App Import" "python -c 'from src.web.api import app; print(app)' > /dev/null 2>&1"

# Generate SSL certificates for testing
if command -v openssl > /dev/null 2>&1; then
    echo -e "\n${YELLOW}Generating SSL certificates for testing...${NC}"
    chmod +x scripts/generate_ssl_certs.sh
    ./scripts/generate_ssl_certs.sh > /dev/null 2>&1
    
    run_test "SSL Certificate Generation" "test -f nginx/ssl/cert.pem && test -f nginx/ssl/key.pem"
fi

# Test 18: Start production container with SSL
echo -e "\n${YELLOW}Testing production deployment with SSL...${NC}"
docker-compose -f docker-compose.production.yml up -d > /dev/null 2>&1

# Wait for containers to start
sleep 15

# Test 19: Check production containers
run_test "Production Containers Running" "docker ps --filter 'name=recall-web-prod' --filter 'status=running' | grep -q recall && docker ps --filter 'name=recall-nginx' --filter 'status=running' | grep -q nginx"

# Test 20: Test HTTPS endpoint (if SSL is configured)
if test -f nginx/ssl/cert.pem; then
    run_test "HTTPS Endpoint" "curl -k -f https://localhost/api/status > /dev/null 2>&1"
fi

# Test 21: Test HTTP to HTTPS redirect
run_test "HTTP to HTTPS Redirect" "curl -I http://localhost 2>/dev/null | grep -q '301'"

# Cleanup production containers
echo -e "\n${YELLOW}Cleaning up production containers...${NC}"
docker-compose -f docker-compose.production.yml down > /dev/null 2>&1

# Test 22: Check Kubernetes manifests
run_test "Kubernetes Manifests" "test -f kubernetes/deployment.yaml"

# Test 23: Validate Kubernetes YAML
if command -v kubectl > /dev/null 2>&1; then
    run_test "Kubernetes YAML Validation" "kubectl apply --dry-run=client -f kubernetes/deployment.yaml > /dev/null 2>&1"
fi

# Final results
echo -e "\n=============================="
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
echo -e "=============================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Deployment is ready.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Please check the output above.${NC}"
    exit 1
fi 