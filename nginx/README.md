# Nginx Configuration Overview

## Files Structure

```
nginx/
├── nginx.conf          # Main Nginx configuration
├── mime.types          # MIME types definitions
├── conf.d/
│   └── erie.conf      # Lake Erie app-specific configuration
├── ssl/               # SSL certificates directory
│   └── README.md
└── logs/              # Nginx access and error logs (auto-created)
```

## Configuration Summary

### Main Configuration (nginx.conf)

**Key Settings:**
- **Worker processes**: Auto-scaled based on CPU cores
- **Worker connections**: 1024 per worker
- **Client max body size**: 10M (for file uploads)
- **Keepalive timeout**: 65 seconds

**Security Features:**
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: no-referrer-when-downgrade

**Performance Features:**
- Gzip compression enabled
- Sendfile enabled
- TCP optimizations (tcp_nopush, tcp_nodelay)

**Rate Limiting Zones:**
- `general`: 10 requests/second
- `api`: 5 requests/second (for optimization endpoint)
- Connection limit: 10 concurrent per IP

### App Configuration (erie.conf)

**Upstream Backend:**
- Server: `model:8000` (matches docker-compose service name)
- Max fails: 3 attempts
- Fail timeout: 30 seconds
- Keepalive: 32 connections
- Keepalive timeout: 65 seconds

**Endpoints:**

1. **Root (/)** - General application
   - Rate limit: 10 req/s + 20 burst
   - Timeout: 60 seconds
   
2. **/run-optimization** - Optimization API
   - Rate limit: 5 req/s + 5 burst
   - Timeout: 300 seconds (5 minutes for long calculations)
   - Enhanced buffering for large responses
   
3. **/health** - Health check
   - No rate limiting
   - No logging to reduce noise

**Security:**
- Blocks access to hidden files (., .env, .git, etc.)
- Blocks sensitive file extensions (.sql, .bak, .log, etc.)
- Connection limit: 10 concurrent per IP
- Proper proxy headers forwarding

## Testing the Configuration

Run the test script:
```bash
./test-nginx.sh
```

This validates:
- Syntax correctness
- Required files existence
- Configuration structure
- Security settings
- Rate limiting setup

## Common Issues and Solutions

### Issue: "host not found in upstream"
**When:** Testing nginx config outside docker-compose
**Solution:** This is expected. The `model` hostname only exists within the docker network. Deploy with docker-compose to resolve.

### Issue: "mime.types not found"
**When:** Custom nginx.conf doesn't have mime.types
**Solution:** We provide custom `mime.types` file mounted at `/etc/nginx/custom/mime.types`

### Issue: Rate limiting too strict
**Solution:** Adjust in `nginx.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=20r/s;  # Increase rate
```

### Issue: Optimization timeout
**Solution:** Increase timeout in `erie.conf`:
```nginx
proxy_read_timeout 600s;  # 10 minutes
```

## Monitoring

### View Access Logs
```bash
# Real-time
tail -f nginx/logs/erie_access.log

# Docker compose
docker-compose logs -f nginx
```

### View Error Logs
```bash
# Real-time
tail -f nginx/logs/erie_error.log

# Docker compose
docker-compose exec nginx tail -f /var/log/nginx/erie_error.log
```

### Check Nginx Status
```bash
docker-compose exec nginx nginx -t  # Test config
docker-compose exec nginx nginx -s reload  # Reload config
```

## Performance Tuning

### For High Traffic
Edit `nginx.conf`:
```nginx
worker_connections 2048;  # Increase connections
keepalive_timeout 30;     # Reduce keepalive
```

### For Large Uploads
Edit `nginx.conf`:
```nginx
client_max_body_size 50M;  # Increase max upload size
```

### For Slow Backends
Edit `erie.conf`:
```nginx
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 600s;
```

## Security Recommendations

1. **Enable HTTPS** (see `erie.conf` HTTPS section)
2. **Whitelist trusted IPs** for admin endpoints
3. **Adjust rate limits** based on traffic patterns
4. **Monitor logs** regularly for suspicious activity
5. **Keep Nginx updated**: `docker-compose pull nginx`
6. **Use strong SSL ciphers** (when enabling HTTPS)

## Integration with Fail2ban

Fail2ban monitors these Nginx logs:
- `/var/log/nginx/erie_access.log`
- `/var/log/nginx/erie_error.log`

It automatically bans IPs that:
- Exceed rate limits
- Make malformed requests
- Search for vulnerabilities
- Generate excessive 4xx errors

See `fail2ban/config/jail.d/nginx.conf` for details.

## Reload Configuration

After making changes:

```bash
# Test configuration first
./test-nginx.sh

# Reload without downtime
docker-compose exec nginx nginx -s reload

# Or restart container
docker-compose restart nginx
```

## References

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx Rate Limiting Guide](https://www.nginx.com/blog/rate-limiting-nginx/)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
