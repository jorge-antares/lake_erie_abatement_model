# SSL Certificates Directory

This directory is for SSL/TLS certificates for HTTPS support.

## For Development/Testing

Generate self-signed certificates:
```bash
./manage.sh generate-ssl
```

Or manually:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

## For Production

Use Let's Encrypt for free, valid SSL certificates:

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

Or use Docker-based certbot:
```bash
docker run -it --rm \
  -v $(pwd)/nginx/ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone -d yourdomain.com
```

## Security Notes

- **NEVER commit private keys (.key, .pem) to version control**
- Keep certificate files secure (600 permissions)
- Renew certificates before expiration (Let's Encrypt = 90 days)
- Use strong ciphers in Nginx configuration

## Files Required

- `cert.pem` - SSL certificate (public)
- `key.pem` - Private key (keep secure!)

These files are referenced in `nginx/conf.d/erie.conf`
