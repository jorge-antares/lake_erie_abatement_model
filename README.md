# Lake Erie Abatement Optimization #

## Description
We present an optimization model for the Canadian side of Lake Erie (LE) that determines the required abatement of total phosphorus (TP) on agricultural activities or end-of-pipe investments in wastewater treatment plants across the Canadian LE watersheds, such that a target reduction in P concentration is achieved at the lowest cost.

The hydrological model used in this study considers the interdependence among six regions: St. Claire River and Lake, the Detroit River, and the Western, Central and Eastern Basins of LE.

### Target-Based Model
The optimization model is:

$$\min_{x,w}\quad x^T A x + b^T w$$

subject to:

$$Sx + Ww ≥ z_{\rm Target}$$

$$x \geq 0$$

$$w_i \in \{0,1\}\quad \forall\ i$$

and its parameters are:

- $A$: diagonal matrix of size $R \times R$ containing the quadratic terms of the cost function in equation 4 in $[\text{CAD  year}/t^2]$.
- $S$: the system matrix of equation 1 in $[10^{-15}$ year/L].
- $z_{\rm Target}$: the target concentration reduction in [ppb].
- $b_i$: the annual maintenance and annual prorated net present value of the investment of installing the filter on WWTP i for a period of one year considering a filter lifetime of T years in [CAD/year].
- $L$: an indicator matrix of size $R \times I$ whose elements $l_{r,i}=1$ if WWTP i is located in region r and zero otherwise [unitless].
- $F$: a diagonal matrix of size $I \times I$ whose diagonal elements $f_{i,i}$ are the TP decrease on the discharge of WWTP i in [t/year].

### Budget-Based Model
This model has the same variables and parameters as Model I but has an additional parameter, $\alpha$, which expresses the relative weight or importance of concentration reductions on each region of the model. The objective function of Model I is introduced here as a constraint, and the phosphorus concentration constraint of Model I is introduced as the objective function.

$$\max_{x,w}\quad \alpha^{\rm T} \big( Sx + Ww \big)$$

subject to:

$$x^{T} A x + b^{T} w  \leq \text{budget}$$

$$x \geq 0$$

$$w_{i} \in \{0,1\}\quad \forall i.$$

---

## Quick Start

### Using Docker (Recommended)

```bash
# 1. Run model
docker run 

# 2. Start all services (FastAPI + Nginx + Fail2ban)
./manage.sh start

# 3. Access the web interface
# Open browser: http://localhost
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Access the web interface
# Open browser: http://localhost:8000
```

## Architecture

The application uses a three-tier architecture with security:

```
Internet → Nginx (Port 80/443) → FastAPI (Port 8000)
              ↓
         Fail2ban (Security)
```

- **FastAPI**: Web application serving the optimization model
- **Nginx**: Reverse proxy with rate limiting and security headers
- **Fail2ban**: Intrusion prevention system to ban malicious IPs


See [QUICKSTART.md](QUICKSTART.md) for more commands.

## Security Features

- **Rate Limiting**: Prevents API abuse (10 req/s general, 5 req/s optimization)
- **Fail2ban Protection**: Automatic IP banning for malicious activity
- **Security Headers**: X-Frame-Options, CSP, XSS Protection
- **Request Filtering**: Blocks common exploit attempts
- **Connection Limiting**: Max 10 concurrent connections per IP

## Project Structure

```
.
├── api
│   ├── app.py                # API Server
│   ├── requirements.txt
│   ├── static
│   │   ├── css
│   │   │   ├── bootstrap-icons.css
│   │   │   └── bootstrap.min.css
│   │   ├── img
│   │   │   └── function.svg
│   │   └── js
│   └── templates
│       ├── base.html
│       ├── index.html
│       ├── model_docs.html
│       ├── optimize.html
│       └── results.html
├── docker-compose.yaml
├── Dockerfile
├── eriemodel                 # Core model implementation
│   ├── __init__.py
│   ├── basemodels.py
│   ├── erieparams.py
│   ├── mod_requirements.txt
│   ├── scenarios.py
│   ├── test.py
│   └── wwtpdata
│       ├── fvec.csv
│       └── Lmat.csv
├── fail2ban                  # Bans malicious requests
│   ├── config
│   ├── filter.d
│   │   ├── nginx-400.conf
│   │   ├── nginx-403.conf
│   │   └── nginx-post-limit.conf
│   ├── jail.d
│   │   └── nginx.conf
│   └── jail.local
├── Makefile
├── nginx                     # Reverse proxy to handle requests
│   ├── conf.d
│   │   └── erie.conf
│   ├── mime.types
│   ├── nginx.conf
│   └── ssl
├── NGINX_FAIL2BAN_SETUP.md
└── README.md
```


## Requirements

- Python 3.8+
- Docker & Docker Compose

## License

MIT License

## 👥 Contributors

[Add contributor information here]


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
