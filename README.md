# Lake Erie Abatement Model (LEAM) #

## Description
This repository contains the Lake Erie Abatement Model (LEAM) and a user interface built on FastAPI to communicate with it, as well as two additional services (Nginx, fail2ban) for hosting the interface on the web.

## LEAM
LEAM is an quadratic program for the Canadian side of Lake Erie that determines the required abatement of total phosphorus on agricultural activities or end-of-pipe investments in wastewater treatment plants across the Canadian LE watersheds, such that a target reduction in P concentration is achieved at the lowest cost. An alternative formulation is presented where the model maximizes the P concentration reduction given a fixed budget to allocate on abatement measures.

The hydrological model used in this study considers the interdependence among six regions:
- St. Claire River
- St. Claire Lake
- the Detroit River
- the Western Basin of Lake Erie
- the Central Basin of Lake Erie
- the Eastern Basin of Lake Erie

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
docker compose up -d
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r api/requirements.txt

# 3. Run the application
cd api
python app.py

# 4. Access the application at http://localhost:8000
```

## Architecture
The application uses a three-tier architecture with security:

- **FastAPI**: Web application serving the optimization model
- **Nginx**: Reverse proxy with rate limiting and security headers
- **Fail2ban**: Intrusion prevention system to ban malicious IPs


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


## License

MIT License

## Contributors

[Add contributor information here]

## Acknowledgements

[Add acknowledgements here]