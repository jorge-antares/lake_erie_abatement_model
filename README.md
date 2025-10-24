# Lake Erie Abatement Optimization #

We present an optimization model for the Canadian side of Lake Erie (LE) that determines the required abatement of total phosphorus (TP) on agricultural activities or end-of-pipe investments in wastewater treatment plants across the Canadian LE watersheds, such that a target reduction in P concentration is achieved at the lowest cost.

The hydrological model used in this study considers the interdependence among six regions: St. Claire River and Lake, the Detroit River, and the Western, Central and Eastern Basins of LE.

# Model I
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

# Model II (Alt)
This model has the same variables and parameters as Model I but has an additional parameter, $\alpha$, which expresses the relative weight or importance of concentration reductions on each region of the model. The objective function of Model I is introduced here as a constraint, and the phosphorus concentration constraint of Model I is introduced as the objective function.

$$\max_{x,w}\quad \alpha^{\rm T} \big( Sx + Ww \big)$$

subject to:

$$x^{T} A x + b^{T} w  \leq \text{budget}$$

$$x \geq 0$$

$$w_{i} \in \{0,1\}\quad \forall i.$$

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# 1. Setup environment
./manage.sh setup

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

## 🏗️ Architecture

The application uses a three-tier architecture with security:

```
Internet → Nginx (Port 80/443) → FastAPI (Port 8000)
              ↓
         Fail2ban (Security)
```

- **FastAPI**: Web application serving the optimization model
- **Nginx**: Reverse proxy with rate limiting and security headers
- **Fail2ban**: Intrusion prevention system to ban malicious IPs

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in minutes
- **[Nginx + Fail2ban Setup](NGINX_FAIL2BAN_SETUP.md)** - Detailed security configuration
- **[SSL/TLS Setup](nginx/ssl/README.md)** - Configure HTTPS

## 🛠️ Management Commands

```bash
./manage.sh start          # Start all services
./manage.sh stop           # Stop all services
./manage.sh status         # Check service status
./manage.sh logs           # View logs
./manage.sh banned         # Show banned IPs
./manage.sh unban <IP>     # Unban an IP address
```

See [QUICKSTART.md](QUICKSTART.md) for more commands.

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse (10 req/s general, 5 req/s optimization)
- **Fail2ban Protection**: Automatic IP banning for malicious activity
- **Security Headers**: X-Frame-Options, CSP, XSS Protection
- **Request Filtering**: Blocks common exploit attempts
- **Connection Limiting**: Max 10 concurrent connections per IP

## 📦 Project Structure

```
lake_erie_model/
├── app.py                    # FastAPI application
├── docker-compose.yaml       # Container orchestration
├── manage.sh                 # Management script
├── src/                      # Optimization model code
│   ├── basemodels.py        # Core optimization functions
│   ├── erieparams.py        # Model parameters
│   └── scenarios.py         # Predefined scenarios
├── templates/               # HTML templates
├── nginx/                   # Nginx configuration
└── fail2ban/                # Security configuration
```

## 🌐 Web Interface

The application provides an intuitive web interface:

1. **Home Page**: Model overview and documentation
2. **Optimization Page**: Interactive parameter input form
3. **Results Page**: Detailed optimization results and visualizations

## 🔧 Requirements

- Python 3.8+
- Docker & Docker Compose (for containerized deployment)
- SCIP Optimization Suite (included in PySCIPOpt)

## 📊 Features

- Two optimization models (target-based and budget-based)
- Interactive web interface with Bootstrap styling
- Customizable parameters (filter efficiency, costs, targets)
- Comprehensive results visualization
- Production-ready with Nginx reverse proxy
- Built-in security with Fail2ban

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 📧 Contact

[Add contact information here]
