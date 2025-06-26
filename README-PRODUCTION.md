# CyberScope Enterprise - Production Deployment Guide

## Overview

CyberScope Enterprise is a production-ready log analytics platform designed for large-scale enterprise deployment. This guide covers production deployment, configuration, and maintenance.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+
- 4+ CPU cores, 8GB+ RAM
- 100GB+ storage

### 1. Enterprise Setup Wizard

Run the interactive setup wizard:

```bash
python setup-wizard.py
```

The wizard will configure:
- Database connections
- Security settings
- AI/ML models
- Monitoring
- User management
- Deployment options

### 2. Environment Configuration

Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Deploy with Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initial Setup

```bash
# Create admin user
python create_admin.py

# Initialize database
docker-compose exec backend alembic upgrade head

# Start AI training
docker-compose exec backend python -m backend.ai.local_agent --init
```

## Production Architecture

### Components

1. **Frontend (React + Nginx)**
   - Professional enterprise UI
   - Dark/Light theme support
   - Internationalization (Arabic support)
   - Real-time dashboards

2. **Backend (FastAPI + Python)**
   - RESTful API with OpenAPI docs
   - JWT authentication + RBAC
   - Real-time WebSocket connections
   - Comprehensive audit logging

3. **Local AI Engine**
   - No external API dependencies
   - Scikit-learn + HuggingFace models
   - Self-learning algorithms
   - Anomaly detection + pattern recognition

4. **Database (PostgreSQL)**
   - Time-series optimized storage
   - Configurable retention policies
   - Backup and recovery

5. **Monitoring Stack**
   - Prometheus metrics collection
   - Grafana dashboards
   - Alert manager
   - Health checks

## Security Features

### Authentication & Authorization

- **JWT-based authentication** with configurable expiration
- **Role-based access control (RBAC)** with granular permissions
- **Multi-factor authentication (MFA)** support
- **Account lockout policies** for brute force protection
- **Session management** with secure token handling

### Security Roles

| Role | Permissions |
|------|-------------|
| Admin | Full system access, user management |
| Security Analyst | Security features, audit logs, threat analysis |
| System Operator | Log management, system configuration, AI features |
| Viewer | Read-only access to logs and dashboards |
| Guest | Limited dashboard access |

### Audit Logging

All user actions are logged with:
- User identification
- Action performed
- Resource accessed
- Timestamp and IP address
- Success/failure status
- Detailed context

## AI/ML Capabilities

### Local AI Agent

The system includes a powerful local AI agent that requires no external APIs:

#### Features
- **Anomaly Detection**: Isolation Forest algorithm for real-time anomaly detection
- **Pattern Recognition**: TF-IDF vectorization with clustering
- **Security Analysis**: Threat pattern matching and risk scoring
- **Predictive Analytics**: Time-series forecasting
- **Self-Learning**: Continuous model improvement

#### Models Used
- Isolation Forest (anomaly detection)
- Random Forest (classification)
- DBSCAN (clustering)
- LSTM (optional, time-series)
- DistilBERT (optional, NLP)

### AI Configuration

```python
# AI settings in .env
AI_MODEL_PATH=./models
ANOMALY_THRESHOLD=0.7
RETRAIN_INTERVAL_HOURS=24
ENABLE_AUTO_LEARNING=true
```

## Deployment Options

### 1. Docker Compose (Recommended for single-node)

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Scale specific services
docker-compose up -d --scale backend=3

# Update services
docker-compose pull
docker-compose up -d
```

### 2. Kubernetes (Recommended for multi-node)

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n cyberscope

# Scale deployment
kubectl scale deployment cyberscope-backend --replicas=5 -n cyberscope
```

### 3. Helm Chart (Advanced)

```bash
# Install with Helm
helm install cyberscope ./helm/cyberscope \
  --namespace cyberscope \
  --create-namespace \
  --values values.prod.yaml
```

## Monitoring & Observability

### Prometheus Metrics

The system exposes comprehensive metrics:

- **Application Metrics**: Request rates, response times, error rates
- **AI Metrics**: Model accuracy, prediction confidence, learning progress
- **Security Metrics**: Authentication attempts, threat detections
- **System Metrics**: CPU, memory, disk usage

### Grafana Dashboards

Pre-configured dashboards for:
- System overview and health
- AI/ML model performance
- Security monitoring
- User activity tracking
- Performance analytics

### Alerts

Automated alerts for:
- High error rates
- Security threats
- System resource exhaustion
- AI model accuracy drops
- Service failures

## Scaling & Performance

### Horizontal Scaling

**Backend Services:**
```bash
# Docker Compose
docker-compose up -d --scale backend=3 --scale ai-worker=2

# Kubernetes
kubectl scale deployment cyberscope-backend --replicas=5
```

**Database Scaling:**
- Read replicas for query load
- Partitioning for large datasets
- Connection pooling

### Performance Optimization

1. **Caching Strategy**
   - Redis for session storage
   - Application-level caching
   - Database query optimization

2. **AI Model Optimization**
   - Model pruning and quantization
   - Batch processing for training
   - Incremental learning

3. **Database Tuning**
   - Index optimization
   - Query performance tuning
   - Connection pool sizing

## Security Hardening

### Network Security

```bash
# Configure firewall (example)
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw deny 5432/tcp    # Block direct DB access
```

### SSL/TLS Configuration

```bash
# Generate certificates (example with Let's Encrypt)
certbot certonly --standalone -d your-domain.com

# Update nginx configuration
cp ssl/cert.pem /etc/nginx/ssl/
cp ssl/key.pem /etc/nginx/ssl/
```

### Environment Security

```bash
# Secure environment file
chmod 600 .env
chown root:root .env

# Secure model directory
chmod 755 models/
chown -R app:app models/
```

## Backup & Recovery

### Database Backup

```bash
# Automated daily backup
docker-compose exec database pg_dump -U cyberscope cyberscope > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T database psql -U cyberscope cyberscope < backup_20240101.sql
```

### AI Model Backup

```bash
# Backup AI models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Restore models
tar -xzf models_backup_20240101.tar.gz
```

### Configuration Backup

```bash
# Backup configuration
cp .env .env.backup
cp -r config/ config_backup/
```

## Maintenance

### Regular Tasks

1. **Daily**
   - Check system health
   - Review security logs
   - Monitor AI performance

2. **Weekly**
   - Update security signatures
   - Review user access
   - Check backup integrity

3. **Monthly**
   - Update dependencies
   - Review system performance
   - Capacity planning

### Log Rotation

```bash
# Configure logrotate
cat > /etc/logrotate.d/cyberscope << EOF
/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

### Health Checks

```bash
# System health endpoint
curl http://localhost:8000/health

# AI agent status
curl http://localhost:8000/api/ai/status

# Database connectivity
docker-compose exec backend python -c "from backend.database import engine; print(engine.execute('SELECT 1').scalar())"
```

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   docker-compose logs service-name
   
   # Check configuration
   docker-compose config
   ```

2. **Database Connection Issues**
   ```bash
   # Test connection
   docker-compose exec database psql -U cyberscope -d cyberscope -c "SELECT version();"
   ```

3. **AI Model Loading Errors**
   ```bash
   # Check model files
   ls -la models/
   
   # Reinitialize models
   docker-compose exec backend python -m backend.ai.local_agent --init
   ```

### Log Locations

- Application logs: `./logs/`
- Database logs: `docker-compose logs database`
- Nginx logs: `docker-compose logs nginx`
- AI agent logs: `./logs/ai_agent.log`

## API Documentation

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Use token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/user/profile
```

### AI Analysis

```bash
# Analyze logs
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"log_entries": [{"message": "Failed login", "level": "ERROR"}]}'
```

### Complete API documentation available at: `http://localhost:8000/api/docs`

## Support

For enterprise support and customization:
- Documentation: [Link to docs]
- Issues: [GitHub issues]
- Enterprise support: [Contact information]

---

**Note**: This is a production-grade system. Please review all security settings and configurations before deploying in your environment.