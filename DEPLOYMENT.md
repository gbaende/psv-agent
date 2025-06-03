# 🚀 DealTracker AWS Deployment Guide

This guide will help you deploy DealTracker Sales Agent to AWS EC2 with full automation capabilities.

## 📋 Prerequisites

- AWS Account with EC2 access
- Domain name (optional, for SSL)
- Slack Bot Token and API keys
- OpenAI API key

## 🏗️ Architecture Overview

```
Internet → AWS Load Balancer/CloudFront → EC2 Instance
                                           ├── Nginx (Reverse Proxy)
                                           ├── React Frontend (Port 3000)
                                           ├── FastAPI Backend (Port 8000)
                                           ├── PostgreSQL Database (Port 5432)
                                           └── Sales Agent Scheduler (Background)
```

## 🚀 Quick Deployment (Staging)

### Step 1: Launch EC2 Instance

1. **Launch EC2 Instance:**

   - Instance Type: `t3.small` or larger (minimum 2GB RAM)
   - AMI: Amazon Linux 2
   - Storage: 20GB+ EBS volume
   - Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **Connect to your instance:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   ```

### Step 2: Clone Repository

```bash
# Clone your repository
git clone https://github.com/your-username/dealtracker.git /home/ec2-user/dealtracker
cd /home/ec2-user/dealtracker
```

### Step 3: Configure Environment

1. **Create production environment file:**

   ```bash
   cp .env.production .env.prod
   nano .env.prod
   ```

2. **Fill in your actual values:**

   ```bash
   # Database Configuration
   POSTGRES_PASSWORD=your_secure_database_password_here

   # OpenAI Configuration
   OPENAI_API_KEY=sk-proj-your-openai-key-here

   # Slack Configuration
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
   SLACK_SIGNING_SECRET=your_slack_signing_secret_here
   SLACK_CHANNEL_ID=your_slack_channel_id_here

   # JWT Configuration
   SECRET_KEY=your_very_secure_jwt_secret_key_here_minimum_32_characters

   # Frontend Configuration (use your EC2 public IP for staging)
   REACT_APP_API_URL=http://your-ec2-public-ip:80
   ```

### Step 4: Deploy

```bash
# Run the deployment script
./deploy-aws.sh
```

The script will:

- ✅ Install Docker and Docker Compose
- ✅ Build and start all services
- ✅ Configure systemd for auto-restart
- ✅ Set up health checks
- ✅ Enable the sales agent scheduler

### Step 5: Verify Deployment

1. **Check service status:**

   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **View logs:**

   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

3. **Test the application:**
   - Frontend: `http://your-ec2-ip:80`
   - Backend API: `http://your-ec2-ip:8000/docs`
   - Health Check: `http://your-ec2-ip:80/health`

## 🔒 Production Setup (with SSL)

### Step 1: Configure Domain

1. **Point your domain to EC2:**

   - Create an A record pointing to your EC2 public IP
   - Wait for DNS propagation (5-30 minutes)

2. **Update environment:**
   ```bash
   nano .env.prod
   ```
   ```bash
   REACT_APP_API_URL=https://your-domain.com
   DOMAIN_NAME=your-domain.com
   SSL_EMAIL=your-email@domain.com
   ```

### Step 2: Enable SSL

1. **Install Certbot:**

   ```bash
   sudo yum install certbot python3-certbot-nginx -y
   ```

2. **Get SSL certificate:**

   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Update nginx configuration:**

   - Edit `nginx.prod.conf`
   - Uncomment the HTTPS server block
   - Update `server_name` to your domain

4. **Restart services:**
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

## 🔧 Management Commands

### Service Management

```bash
# Check status
sudo systemctl status dealtracker

# Start/Stop/Restart
sudo systemctl start dealtracker
sudo systemctl stop dealtracker
sudo systemctl restart dealtracker

# View logs
sudo journalctl -u dealtracker -f
```

### Docker Management

```bash
# View running containers
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f [service_name]

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Update and redeploy
git pull origin main
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Database Management

```bash
# Access database
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d dealtracker

# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres dealtracker > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres dealtracker < backup.sql
```

## 📊 Monitoring

### Health Checks

- **Nginx:** `curl http://localhost:80/health`
- **Backend:** `curl http://localhost:8000/api/health`
- **Database:** `docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres`

### Scheduler Status

```bash
# Check scheduler jobs
curl http://localhost:8000/api/sales/scheduler/status | jq
```

### Log Locations

- **Application logs:** `/home/ec2-user/dealtracker/logs/`
- **Nginx logs:** `docker-compose logs nginx`
- **Backend logs:** `docker-compose logs backend`
- **Database logs:** `docker-compose logs db`

## 🔐 Security Considerations

### AWS Security Group Rules

```
Type        Protocol    Port Range    Source
SSH         TCP         22           Your IP only
HTTP        TCP         80           0.0.0.0/0
HTTPS       TCP         443          0.0.0.0/0
```

### Environment Security

- ✅ Never commit `.env.prod` to version control
- ✅ Use strong passwords (minimum 32 characters)
- ✅ Rotate API keys regularly
- ✅ Enable AWS CloudTrail for audit logging
- ✅ Use IAM roles instead of access keys when possible

## 🚨 Troubleshooting

### Common Issues

1. **Services won't start:**

   ```bash
   # Check Docker daemon
   sudo systemctl status docker

   # Check disk space
   df -h

   # Check memory
   free -h
   ```

2. **Database connection errors:**

   ```bash
   # Check database logs
   docker-compose -f docker-compose.prod.yml logs db

   # Verify environment variables
   docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE
   ```

3. **Scheduler not working:**

   ```bash
   # Check backend logs for scheduler messages
   docker-compose -f docker-compose.prod.yml logs backend | grep SCHEDULER

   # Verify scheduler status
   curl http://localhost:8000/api/sales/scheduler/status
   ```

4. **Frontend not loading:**

   ```bash
   # Check nginx logs
   docker-compose -f docker-compose.prod.yml logs nginx

   # Verify frontend build
   docker-compose -f docker-compose.prod.yml exec frontend ls -la /usr/share/nginx/html
   ```

### Performance Optimization

1. **Scale up EC2 instance** if needed (t3.medium, t3.large)
2. **Add CloudFront** for global CDN
3. **Use RDS** for managed database in production
4. **Enable log rotation** to prevent disk space issues

## 🎯 Features Enabled

✅ **Sales Agent Scheduler** - Automated prompts and follow-ups  
✅ **Slack Integration** - Real-time team communication  
✅ **Goal Tracking** - Weekly targets and progress monitoring  
✅ **Leaderboards** - Team performance rankings  
✅ **Health Monitoring** - Service status and alerts  
✅ **Auto-restart** - Systemd ensures 24/7 uptime  
✅ **Database Persistence** - Data survives container restarts  
✅ **SSL Ready** - Production-grade security

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Verify all environment variables are set correctly
4. Ensure AWS security groups allow required traffic

Your DealTracker Sales Agent is now running 24/7 with full automation! 🎉
