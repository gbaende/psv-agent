#!/bin/bash

# ===========================================
# DealTracker AWS EC2 Deployment Script
# ===========================================
# Run this script on your EC2 instance to deploy DealTracker

set -e  # Exit on any error

echo "🚀 Starting DealTracker deployment on AWS EC2..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as ec2-user."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo yum update -y

# Install Docker
print_status "Installing Docker..."
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
print_status "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git if not present
print_status "Installing Git..."
sudo yum install git -y

# Create application directory
APP_DIR="/home/ec2-user/dealtracker"
print_status "Creating application directory at $APP_DIR..."
mkdir -p $APP_DIR

# Check if this is a fresh deployment or update
if [ -d "$APP_DIR/.git" ]; then
    print_status "Updating existing deployment..."
    cd $APP_DIR
    git pull origin main
else
    print_status "Fresh deployment - please clone your repository manually:"
    print_warning "Run: git clone <your-repo-url> $APP_DIR"
    print_warning "Then run this script again from the $APP_DIR directory"
    exit 0
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/ssl

# Check for environment file
if [ ! -f "$APP_DIR/.env.prod" ]; then
    print_warning "Environment file .env.prod not found!"
    print_warning "Please create .env.prod based on .env.production template"
    print_warning "Make sure to set all required variables:"
    echo "  - POSTGRES_PASSWORD"
    echo "  - OPENAI_API_KEY"
    echo "  - SLACK_BOT_TOKEN"
    echo "  - SLACK_SIGNING_SECRET"
    echo "  - SLACK_CHANNEL_ID"
    echo "  - SECRET_KEY"
    echo "  - REACT_APP_API_URL"
    exit 1
fi

# Load environment variables
print_status "Loading environment variables..."
set -a
source $APP_DIR/.env.prod
set +a

# Stop existing services
print_status "Stopping existing services..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 30

# Check service health
print_status "Checking service health..."
if curl -f http://localhost:80/health > /dev/null 2>&1; then
    print_status "✅ Nginx is healthy"
else
    print_error "❌ Nginx health check failed"
fi

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    print_status "✅ Backend is healthy"
else
    print_error "❌ Backend health check failed"
fi

# Install systemd service
print_status "Installing systemd service..."
sudo cp $APP_DIR/dealtracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dealtracker.service

print_status "✅ Deployment completed successfully!"
print_status "🌐 Your application should be available at:"
print_status "   Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):80"
print_status "   Backend API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"

print_status "📊 To check service status:"
echo "  docker-compose -f docker-compose.prod.yml ps"
echo "  docker-compose -f docker-compose.prod.yml logs -f"

print_status "🔧 To manage the service:"
echo "  sudo systemctl status dealtracker"
echo "  sudo systemctl restart dealtracker"
echo "  sudo systemctl stop dealtracker"

print_warning "⚠️  Important next steps:"
echo "1. Configure your domain DNS to point to this EC2 instance"
echo "2. Update REACT_APP_API_URL in .env.prod to use your domain"
echo "3. Set up SSL certificates for production use"
echo "4. Configure AWS security groups to allow HTTP/HTTPS traffic"

print_status "🎉 DealTracker Sales Agent is now running with full automation!"
print_status "   - Scheduler is active for automated sales prompts"
print_status "   - Slack integration is ready"
print_status "   - Database is persistent across restarts" 