# SSL Certificate Setup - ZeroSSL Validation

## Overview

This document explains the SSL certificate validation setup for the Lake Erie Optimization application using ZeroSSL.

## Validation Endpoint

The application serves a ZeroSSL validation file at:
```
http://35.192.6.155/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt
```

## File Structure

```
api/
└── static/
    └── .well-known/
        └── pki-validation/
            └── 29EBA45A209B442CDB584C17035B3780.txt
```

## Implementation

### 1. FastAPI Endpoint

The validation file is served through a dedicated endpoint in `api/app.py`:

```python
@app.get("/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt", response_class=PlainTextResponse)
async def ssl_validation():
    """Serve ZeroSSL validation file"""
    validation_file = os.path.join(os.path.dirname(__file__), "static", ".well-known", "pki-validation", "29EBA45A209B442CDB584C17035B3780.txt")
    try:
        with open(validation_file, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Validation file not found")
```

### 2. Nginx Configuration

Nginx routes the validation request to the backend in `nginx/conf.d/erie.conf`:

```nginx
# SSL validation (no rate limiting)
location /.well-known/pki-validation/ {
    proxy_pass http://erie_backend;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    access_log off;
}
```

**Key features:**
- No rate limiting applied
- No logging to reduce noise
- Direct pass-through to backend

## Testing

### Local Testing

Run the test script:
```bash
./test-ssl-validation.sh
```

This will:
1. Test direct access to FastAPI endpoint
2. Test through Nginx proxy
3. Verify content matches the file

### Manual Testing

```bash
# Test locally
curl http://localhost/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt

# Test on production server
curl http://35.192.6.155/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt
```

Expected response:
```
55995544A3B873729454E93929C319838F6EC45004183D82FEB6FC3AB7A9EDA0
comodoca.com
d8ffa60407419a0
```

## Deployment Steps

1. **Ensure the validation file exists:**
   ```bash
   ls -la api/static/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt
   ```

2. **Rebuild and deploy:**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

3. **Verify the endpoint:**
   ```bash
   curl http://35.192.6.155/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt
   ```

4. **Complete ZeroSSL validation:**
   - Go to ZeroSSL dashboard
   - Click "Verify Domain"
   - ZeroSSL will check the validation file
   - Once verified, download the certificates

## After Validation Success

Once ZeroSSL validates successfully:

1. **Download certificates** from ZeroSSL dashboard
2. **Copy certificates to server:**
   ```bash
   scp certificate.crt your-server:/path/to/lake_erie_model/nginx/ssl/cert.pem
   scp private.key your-server:/path/to/lake_erie_model/nginx/ssl/key.pem
   scp ca_bundle.crt your-server:/path/to/lake_erie_model/nginx/ssl/ca-bundle.pem
   ```

3. **Enable HTTPS in Nginx:**
   - Uncomment the HTTPS server block in `nginx/conf.d/erie.conf`
   - Update `server_name` to your domain
   - Restart Nginx:
     ```bash
     docker-compose restart nginx
     ```

4. **Test HTTPS:**
   ```bash
   curl https://35.192.6.155/health
   ```

## Troubleshooting

### Validation file not found (404)

**Symptoms:**
```bash
curl http://localhost/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt
# Returns 404
```

**Solution:**
1. Check file exists:
   ```bash
   ls -la api/static/.well-known/pki-validation/
   ```

2. Rebuild container:
   ```bash
   docker-compose build model
   docker-compose up -d model
   ```

3. Check FastAPI endpoint directly:
   ```bash
   curl http://localhost:8000/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt
   ```

### Nginx not routing correctly

**Symptoms:**
- FastAPI endpoint works directly (port 8000)
- But Nginx proxy returns error (port 80)

**Solution:**
1. Check Nginx configuration:
   ```bash
   ./test-nginx.sh
   ```

2. Check Nginx logs:
   ```bash
   docker-compose logs nginx
   ```

3. Restart Nginx:
   ```bash
   docker-compose restart nginx
   ```

### Permission issues

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solution:**
1. Check file permissions:
   ```bash
   ls -la api/static/.well-known/pki-validation/
   ```

2. Ensure file is readable:
   ```bash
   chmod 644 api/static/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt
   ```

3. Rebuild container:
   ```bash
   docker-compose build model
   docker-compose up -d
   ```

## Security Notes

- The validation file contains a public token - it's safe to serve publicly
- The endpoint has no rate limiting to ensure ZeroSSL can always access it
- No authentication is required (by design for SSL validation)
- The endpoint is only needed during the validation process
- After SSL is set up, you can keep or remove the endpoint

## Alternative: Direct File Serving

If you prefer to serve the file directly through Nginx instead of FastAPI:

1. **Mount validation directory in docker-compose.yaml:**
   ```yaml
   nginx:
     volumes:
       - ./ssl-validation/.well-known:/usr/share/nginx/html/.well-known:ro
   ```

2. **Add Nginx location block:**
   ```nginx
   location /.well-known/pki-validation/ {
       root /usr/share/nginx/html;
       try_files $uri =404;
   }
   ```

3. **Place file:**
   ```bash
   mkdir -p ssl-validation/.well-known/pki-validation/
   cp 29EBA45A209B442CDB584C17035B3780.txt ssl-validation/.well-known/pki-validation/
   ```

## References

- [ZeroSSL Documentation](https://zerossl.com/documentation/)
- [HTTP-01 Challenge](https://letsencrypt.org/docs/challenge-types/#http-01-challenge)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
