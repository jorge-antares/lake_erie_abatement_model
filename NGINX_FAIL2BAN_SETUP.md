# Nginx and Fail2ban Security Setup

## Overview

This Docker Compose setup includes:
- **FastAPI Application**: The Lake Erie optimization model backend
- **Nginx**: Reverse proxy with rate limiting and security headers
- **Fail2ban**: Intrusion prevention system to ban malicious IPs

## Architecture

```
Internet → Nginx (Port 80/443) → FastAPI (Port 8000)
                ↓
           Fail2ban (monitors logs)
```

## Services

### 1. Nginx Reverse Proxy
- **Image**: nginx:alpine
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Features**:
  - Rate limiting (10 req/s general, 5 req/s for optimization endpoints)
  - Connection limiting (10 concurrent per IP)
  - Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
  - Gzip compression
  - Request logging for Fail2ban
  - Blocks common exploit attempts

### 2. Fail2ban Security
- **Image**: crazymax/fail2ban:latest
- **Features**:
  - Monitors Nginx logs for suspicious activity
  - Automatically bans malicious IPs
  - Multiple jails configured:
    - HTTP authentication failures
    - Rate limit violations
    - Bot searches
    - Malformed requests
    - 403/404 abuse
    - DDoS attempts

### 3. FastAPI Application
- Runs on internal network
- Not directly exposed to internet
- Only accessible through Nginx proxy

## Configuration

### Nginx Configuration Files
- `nginx/nginx.conf` - Main Nginx configuration
- `nginx/conf.d/erie.conf` - Lake Erie app-specific configuration

### Fail2ban Configuration Files
- `fail2ban/config/jail.local` - Global Fail2ban settings
- `fail2ban/config/jail.d/nginx.conf` - Nginx-specific jails
- `fail2ban/config/filter.d/*.conf` - Custom filter definitions

### Key Security Features

#### Rate Limiting
- General endpoints: 10 requests/second with burst of 20
- Optimization endpoint: 5 requests/second with burst of 5
- Connection limit: 10 concurrent connections per IP

#### Ban Settings (Default)
- **Ban time**: 1 hour (3600s)
- **Find time**: 10 minutes (600s)
- **Max retry**: 5 attempts
- Longer bans for severe violations (up to 24 hours)

## Usage

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# Nginx logs
docker-compose logs -f nginx

# Fail2ban logs
docker-compose logs -f fail2ban

# Application logs
docker-compose logs -f server
```

### Check Fail2ban Status
```bash
# Access fail2ban container
docker exec -it erie_fail2ban sh

# Check banned IPs
fail2ban-client status

# Check specific jail
fail2ban-client status nginx-limit-req

# Unban an IP
fail2ban-client set nginx-limit-req unbanip <IP_ADDRESS>
```

### Monitor Real-time Access
```bash
# Nginx access logs
tail -f logs/nginx/erie_access.log

# Nginx error logs
tail -f logs/nginx/erie_error.log
```

### Adjust Rate Limits
Edit `nginx/conf.d/erie.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=5r/s;
```

### Modify Ban Settings
Edit `fail2ban/config/jail.local`:
```ini
bantime = 3600    # Time IP is banned (seconds)
findtime = 600    # Time window for counting violations (seconds)
maxretry = 5      # Number of violations before ban
```

### Add Custom Fail2ban Rules
1. Create filter in `fail2ban/config/filter.d/`
2. Add jail in `fail2ban/config/jail.d/nginx.conf`
3. Restart Fail2ban: `docker-compose restart fail2ban`
