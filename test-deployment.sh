#!/bin/bash

# ===========================================
# DealTracker Deployment Test Script
# ===========================================
# Run this script to verify your deployment is working correctly

set -e

echo "🧪 Testing DealTracker deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Test functions
test_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    print_info "Testing $service_name at $url"
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_status" ]; then
            print_success "$service_name is responding correctly (HTTP $response)"
            return 0
        else
            print_error "$service_name returned HTTP $response (expected $expected_status)"
            return 1
        fi
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Get EC2 public IP
if command -v curl >/dev/null 2>&1; then
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
else
    PUBLIC_IP="localhost"
fi

print_info "Testing deployment on IP: $PUBLIC_IP"

# Test Docker services
print_info "Checking Docker services..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_success "Docker services are running"
else
    print_error "Docker services are not running properly"
    docker-compose -f docker-compose.prod.yml ps
    exit 1
fi

# Test individual services
echo ""
print_info "Testing service endpoints..."

# Test Nginx health check
test_service "Nginx Health Check" "http://$PUBLIC_IP:80/health"

# Test Backend health check
test_service "Backend Health Check" "http://$PUBLIC_IP:8000/api/health"

# Test Frontend (should return HTML)
if curl -s "http://$PUBLIC_IP:80" | grep -q "DealTracker\|React"; then
    print_success "Frontend is serving content"
else
    print_error "Frontend is not serving expected content"
fi

# Test Backend API documentation
test_service "Backend API Docs" "http://$PUBLIC_IP:8000/docs"

# Test Scheduler status
print_info "Testing Sales Agent Scheduler..."
if scheduler_response=$(curl -s "http://$PUBLIC_IP:8000/api/sales/scheduler/status" 2>/dev/null); then
    if echo "$scheduler_response" | grep -q '"success":true'; then
        job_count=$(echo "$scheduler_response" | grep -o '"jobs":\[[^]]*\]' | grep -o '{' | wc -l)
        print_success "Scheduler is active with $job_count jobs scheduled"
    else
        print_error "Scheduler API returned error"
        echo "$scheduler_response"
    fi
else
    print_error "Could not reach scheduler API"
fi

# Test Database connectivity
print_info "Testing database connectivity..."
if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres >/dev/null 2>&1; then
    print_success "Database is accepting connections"
else
    print_error "Database is not accepting connections"
fi

# Check systemd service
print_info "Checking systemd service..."
if systemctl is-active --quiet dealtracker 2>/dev/null; then
    print_success "Systemd service is active"
else
    print_error "Systemd service is not active"
fi

# Summary
echo ""
print_info "=== Deployment Test Summary ==="
echo "🌐 Frontend URL: http://$PUBLIC_IP:80"
echo "🔧 Backend API: http://$PUBLIC_IP:8000"
echo "📚 API Documentation: http://$PUBLIC_IP:8000/docs"
echo "❤️  Health Check: http://$PUBLIC_IP:80/health"

echo ""
print_info "=== Next Steps ==="
echo "1. Configure your domain DNS (if using a domain)"
echo "2. Set up SSL certificates for production"
echo "3. Update REACT_APP_API_URL in .env.prod"
echo "4. Configure Slack integration"
echo "5. Test the Sales Agent automation features"

echo ""
print_success "🎉 Deployment test completed!" 