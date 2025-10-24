#!/bin/bash

# Lake Erie Model - Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_info "Docker is running"
}

# Start services
start() {
    print_info "Starting Lake Erie Optimization services..."
    docker-compose up -d
    print_info "Services started successfully"
    print_info "Application available at: http://localhost"
    print_info "To view logs: ./manage.sh logs"
}

# Stop services
stop() {
    print_info "Stopping Lake Erie Optimization services..."
    docker-compose down
    print_info "Services stopped successfully"
}

# Restart services
restart() {
    print_info "Restarting Lake Erie Optimization services..."
    docker-compose restart
    print_info "Services restarted successfully"
}

# View logs
logs() {
    if [ -z "$2" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$2"
    fi
}

# Check status
status() {
    print_info "Service status:"
    docker-compose ps
    echo ""
    print_info "Fail2ban status:"
    docker exec erie_fail2ban fail2ban-client status 2>/dev/null || print_warn "Fail2ban container not running"
}

# Show banned IPs
banned() {
    print_info "Banned IPs:"
    docker exec erie_fail2ban fail2ban-client status 2>/dev/null || print_error "Fail2ban container not running"
}

# Unban IP
unban() {
    if [ -z "$2" ]; then
        print_error "Usage: ./manage.sh unban <IP_ADDRESS>"
        exit 1
    fi
    print_info "Unbanning IP: $2"
    docker exec erie_fail2ban fail2ban-client unban "$2"
    print_info "IP $2 has been unbanned"
}

# Test Nginx configuration
test_nginx() {
    print_info "Testing Nginx configuration..."
    docker run --rm -v "$(pwd)/nginx:/etc/nginx" nginx:alpine nginx -t
    print_info "Nginx configuration is valid"
}

# Generate SSL certificates (self-signed)
generate_ssl() {
    print_info "Generating self-signed SSL certificates..."
    mkdir -p nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    print_info "SSL certificates generated in nginx/ssl/"
    print_warn "These are self-signed certificates for testing only"
}

# Backup Fail2ban data
backup() {
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    print_info "Creating backup in $BACKUP_DIR..."
    
    if [ -d "fail2ban/data" ]; then
        cp -r fail2ban/data "$BACKUP_DIR/"
    fi
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/"
    fi
    
    print_info "Backup completed: $BACKUP_DIR"
}

# Clean logs
clean_logs() {
    print_warn "This will remove all log files. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_info "Cleaning logs..."
        rm -rf logs/*
        print_info "Logs cleaned"
    else
        print_info "Cancelled"
    fi
}

# Setup environment
setup() {
    print_info "Setting up Lake Erie Optimization environment..."
    
    # Create necessary directories
    mkdir -p logs/nginx
    mkdir -p nginx/ssl
    mkdir -p fail2ban/data
    
    # Copy example env file if .env doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "Created .env file from .env.example"
            print_warn "Please update .env with your settings"
        fi
    fi
    
    print_info "Setup completed"
    print_info "Run './manage.sh start' to start the services"
}

# Help
show_help() {
    cat << EOF
Lake Erie Optimization Model - Docker Management

Usage: ./manage.sh [command]

Commands:
    start           Start all services
    stop            Stop all services
    restart         Restart all services
    status          Show service status
    logs [service]  View logs (optional: specify service)
    banned          Show banned IPs
    unban <ip>      Unban an IP address
    test-nginx      Test Nginx configuration
    generate-ssl    Generate self-signed SSL certificates
    backup          Backup Fail2ban data and logs
    clean-logs      Remove all log files
    setup           Initial setup (create directories, etc.)
    help            Show this help message

Examples:
    ./manage.sh start
    ./manage.sh logs nginx
    ./manage.sh unban 192.168.1.100
    ./manage.sh status

EOF
}

# Main script
case "$1" in
    start)
        check_docker
        start
        ;;
    stop)
        stop
        ;;
    restart)
        check_docker
        restart
        ;;
    logs)
        logs "$@"
        ;;
    status)
        status
        ;;
    banned)
        banned
        ;;
    unban)
        unban "$@"
        ;;
    test-nginx)
        test_nginx
        ;;
    generate-ssl)
        generate_ssl
        ;;
    backup)
        backup
        ;;
    clean-logs)
        clean_logs
        ;;
    setup)
        setup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
