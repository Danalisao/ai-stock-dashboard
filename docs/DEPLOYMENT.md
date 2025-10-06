# 🚀 Professional Deployment Guide

## Overview

This guide covers professional deployment strategies for the AI Stock Trading Dashboard in production environments.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.10+ (for local development)
- 4GB RAM minimum (8GB recommended)
- Stable internet connection for real-time data

## Quick Start (Docker)

### 1. Build and Run with Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd ai-stock-dashboard

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f trading-platform

# Stop
docker-compose down
```

Access dashboard at: **http://localhost:8501**

### 2. Manual Docker Build

```bash
# Build image
docker build -t ai-stock-dashboard:latest .

# Run container
docker run -d \
  --name stock-dashboard \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  --restart unless-stopped \
  ai-stock-dashboard:latest
```

## Production Deployment

### Environment Variables

Required environment variables for production:

```bash
# Professional Mode (mandatory)
PROFESSIONAL_MODE=true
TRADING_MODE=PROFESSIONAL

# Database
DATABASE_PATH=/app/data/stock_data.db

# Alerts (optional)
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Reddit API (optional)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=StockDashboard/2.0

# Timezone
TZ=UTC
```

### Health Checks

The application includes health check endpoints:

```bash
# Check application health
curl http://localhost:8501/_stcore/health

# View metrics
curl http://localhost:8501/_stcore/metrics
```

### Persistent Data

Mount these volumes for data persistence:

- `/app/data` - Database and cache
- `/app/logs` - Application logs
- `/app/models` - ML models
- `/app/backups` - Database backups

### Backup Strategy

```bash
# Automated backup (runs via cron)
docker exec stock-dashboard python scripts/backup_database.py

# Manual backup
docker cp stock-dashboard:/app/data ./backups/

# Restore
docker cp ./backups/stock_data.db stock-dashboard:/app/data/
```

## Scaling & Performance

### Resource Limits

Recommended Docker resource limits:

```yaml
services:
  trading-platform:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Load Balancing

For high availability:

```bash
# Run multiple instances
docker-compose up --scale trading-platform=3
```

Use nginx or traefik as reverse proxy.

## Monitoring

### Application Logs

```bash
# View live logs
docker-compose logs -f

# Export logs
docker-compose logs > logs/export.log

# Log rotation
# Configured in config.yaml:
#   max_log_size_mb: 10
#   backup_count: 5
```

### System Metrics

Monitor these metrics:

- **CPU Usage**: Should stay below 60%
- **Memory**: Typical usage 1-2GB
- **Network**: ~1-5 MB/min during market hours
- **Disk**: ~100MB growth per month

### Alerts

Configure alert channels in `config.yaml`:

```yaml
alerts:
  enabled: true
  channels:
    desktop: true
    telegram: true
    email: true
    audio: true
```

## Security

### Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **API Keys**: Use read-only keys when possible
3. **Network**: Run behind firewall or VPN
4. **Updates**: Keep dependencies updated
5. **Backups**: Daily automated backups

### Firewall Rules

```bash
# Allow only necessary ports
ufw allow 8501/tcp  # Streamlit
ufw enable
```

### SSL/TLS

Use reverse proxy (nginx) for HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name trading.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs trading-platform

# Validate configuration
docker-compose config

# Rebuild
docker-compose build --no-cache
```

### Professional Mode Errors

```bash
# Run validation
docker exec stock-dashboard python validate_pro_config.py

# Check professional mode status
docker exec stock-dashboard python -c "from modules.pro_mode_guard import ProModeGuard; print('Professional mode active')"
```

### Database Issues

```bash
# Check database integrity
docker exec stock-dashboard sqlite3 /app/data/stock_data.db "PRAGMA integrity_check;"

# Reset database (WARNING: deletes all data)
docker exec stock-dashboard rm /app/data/stock_data.db
docker-compose restart
```

### Performance Issues

```bash
# Check resource usage
docker stats stock-dashboard

# Increase memory limit
docker update --memory 6g stock-dashboard

# Clear cache
docker exec stock-dashboard rm -rf /app/data/cache/*
```

## Maintenance

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Maintenance

```bash
# Vacuum database (optimize)
docker exec stock-dashboard sqlite3 /app/data/stock_data.db "VACUUM;"

# Check size
docker exec stock-dashboard du -h /app/data/stock_data.db
```

### Log Cleanup

```bash
# Remove old logs
docker exec stock-dashboard find /app/logs -name "*.log" -mtime +30 -delete
```

## Advanced Configuration

### Custom Watchlist

Edit `config.yaml`:

```yaml
watchlist:
  stocks:
    - AAPL
    - MSFT
    # ... add your symbols
  max_stocks: 250
  auto_refresh: true
```

### Trading Parameters

```yaml
trading:
  entry_score_min: 85
  min_risk_reward: 2.5
  stop_loss_pct: 8
  take_profit_pct: 25
```

### Alert Thresholds

```yaml
alerts:
  conditions:
    price_change_pct: 5
    volume_surge_multiplier: 2.0
    rsi_oversold: 30
    rsi_overbought: 70
```

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Run validation: `python validate_pro_config.py`
3. Review configuration: `config.yaml`
4. Check system requirements

## License

Professional Trading System - See LICENSE file for details.

---

**Last Updated:** 2025-10-06  
**Version:** 2.0  
**Status:** Production Ready ✅
