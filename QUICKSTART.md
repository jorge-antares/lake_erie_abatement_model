# Quick Start Guide - Nginx + Fail2ban Setup

## 🚀 Quick Start

```bash
# 1. Initial setup (create directories, copy env file)
./manage.sh setup

# 2. Start all services
./manage.sh start

# 3. Access the application
# Open browser: http://localhost
```

## 📁 Project Structure

```
lake_erie_model/
├── docker-compose.yaml          # Main orchestration file
├── manage.sh                    # Management script
├── .env.example                 # Environment template
├── nginx/
│   ├── nginx.conf              # Main Nginx config
│   ├── conf.d/
│   │   └── erie.conf           # App-specific config
│   └── ssl/                    # SSL certificates (create your own)
├── fail2ban/
│   ├── config/
│   │   ├── jail.local          # Main Fail2ban config
│   │   ├── jail.d/
│   │   │   └── nginx.conf      # Nginx jails
│   │   └── filter.d/           # Custom filters
│   └── data/                   # Fail2ban database (auto-created)
└── logs/
    └── nginx/                  # Nginx logs (auto-created)
```

## 🛠️ Management Commands

```bash
./manage.sh start           # Start all services
./manage.sh stop            # Stop all services
./manage.sh restart         # Restart all services
./manage.sh status          # Check service status
./manage.sh logs            # View all logs
./manage.sh logs nginx      # View specific service logs
./manage.sh banned          # Show banned IPs
./manage.sh unban <IP>      # Unban an IP address
./manage.sh backup          # Backup data and logs
./manage.sh test-nginx      # Test Nginx config
./manage.sh generate-ssl    # Generate self-signed SSL
```

## 🔒 Security Features

### Rate Limiting
- **General endpoints**: 10 requests/second
- **Optimization endpoint**: 5 requests/second
- **Connection limit**: 10 concurrent per IP

### Fail2ban Protection
| Jail | Max Retries | Find Time | Ban Time |
|------|-------------|-----------|----------|
| nginx-limit-req | 10 | 60s | 30 min |
| nginx-botsearch | 5 | 10 min | 2 hours |
| nginx-badbots | 3 | 10 min | 24 hours |
| nginx-post-limit | 10 | 60s | 1 hour |
| nginx-403 | 5 | 10 min | 1 hour |
| nginx-400 | 5 | 5 min | 1 hour |

### Security Headers
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: no-referrer-when-downgrade

## 🔧 Common Tasks

### View Real-time Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f fail2ban

# Tail log files directly
tail -f logs/nginx/erie_access.log
```

### Check Banned IPs
```bash
# Show all banned IPs
docker exec erie_fail2ban fail2ban-client status

# Show specific jail status
docker exec erie_fail2ban fail2ban-client status nginx-limit-req
```

### Unban an IP
```bash
# Using management script
./manage.sh unban 192.168.1.100

# Or directly
docker exec erie_fail2ban fail2ban-client set nginx-limit-req unbanip 192.168.1.100
```

### Test Nginx Configuration
```bash
./manage.sh test-nginx
```

### Update Configuration
```bash
# 1. Edit configuration files
vim nginx/conf.d/erie.conf
vim fail2ban/config/jail.d/nginx.conf

# 2. Test (for Nginx)
./manage.sh test-nginx

# 3. Restart affected service
docker-compose restart nginx
docker-compose restart fail2ban
```

## 🌐 Enable HTTPS

### Option 1: Self-Signed (Testing)
```bash
# Generate certificates
./manage.sh generate-ssl

# Uncomment HTTPS section in nginx/conf.d/erie.conf
vim nginx/conf.d/erie.conf

# Restart Nginx
docker-compose restart nginx
```

### Option 2: Let's Encrypt (Production)
```bash
# Install certbot on host
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy to project
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Update nginx/conf.d/erie.conf with your domain
# Restart
docker-compose restart nginx
```

## 📊 Monitoring

### Check Service Health
```bash
# All services
./manage.sh status

# Health check endpoint
curl http://localhost/health
```

### Monitor Access Patterns
```bash
# Real-time access
tail -f logs/nginx/erie_access.log

# Count requests by IP
awk '{print $1}' logs/nginx/erie_access.log | sort | uniq -c | sort -rn | head -10

# Count status codes
awk '{print $9}' logs/nginx/erie_access.log | sort | uniq -c | sort -rn
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs <service_name>

# Check if port is in use
lsof -i :80
lsof -i :443

# Verify Docker is running
docker ps
```

### Nginx configuration error
```bash
# Test configuration
./manage.sh test-nginx

# Check syntax
docker run --rm -v $(pwd)/nginx:/etc/nginx nginx:alpine nginx -t
```

### Fail2ban not working
```bash
# Check logs
docker-compose logs fail2ban

# Test filter
docker exec erie_fail2ban fail2ban-regex /var/log/nginx/erie_access.log /etc/fail2ban/filter.d/nginx-post-limit.conf

# Verify log access
docker exec erie_fail2ban ls -la /var/log/nginx/
```

### Can't access application
```bash
# Check if containers are running
docker-compose ps

# Test backend directly
curl http://localhost:8000/health

# Check Nginx proxy
curl -v http://localhost/health
```

## ⚙️ Configuration Tips

### Adjust Rate Limits
Edit `nginx/conf.d/erie.conf`:
```nginx
# More permissive
limit_req_zone $binary_remote_addr zone=general:10m rate=20r/s;

# More restrictive
limit_req_zone $binary_remote_addr zone=api:10m rate=2r/s;
```

### Customize Ban Times
Edit `fail2ban/config/jail.local`:
```ini
bantime = 7200      # 2 hours
findtime = 300      # 5 minutes
maxretry = 3        # 3 attempts
```

### Whitelist IPs
Edit `fail2ban/config/jail.local`:
```ini
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1 192.168.1.0/24
```

## 📦 Production Deployment

1. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Generate real SSL certificates**
   ```bash
   # Use Let's Encrypt or your certificate provider
   ```

3. **Update domain in Nginx config**
   ```bash
   vim nginx/conf.d/erie.conf
   # Change server_name from localhost to your domain
   ```

4. **Adjust security settings**
   ```bash
   # Review and tighten fail2ban rules
   vim fail2ban/config/jail.d/nginx.conf
   ```

5. **Start services**
   ```bash
   ./manage.sh start
   ```

6. **Set up monitoring**
   - Configure log rotation
   - Set up alerting
   - Monitor resource usage

## 📚 Additional Resources

- [Complete Setup Documentation](NGINX_FAIL2BAN_SETUP.md)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Fail2ban Documentation](https://www.fail2ban.org/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
