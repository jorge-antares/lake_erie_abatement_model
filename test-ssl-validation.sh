#!/bin/bash

# Test SSL Validation Endpoint

echo "Testing SSL validation endpoint..."
echo ""

# Check if containers are running
if ! docker ps | grep -q erie_app; then
    echo "⚠️  Containers are not running. Starting them..."
    docker-compose up -d
    sleep 10
fi

echo "1. Testing direct access to FastAPI endpoint..."
RESPONSE=$(curl -s http://localhost:8000/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt)

if [ -n "$RESPONSE" ]; then
    echo "✓ FastAPI endpoint responds"
    echo "Response: $RESPONSE"
else
    echo "✗ FastAPI endpoint does not respond"
fi

echo ""
echo "2. Testing through Nginx proxy..."
NGINX_RESPONSE=$(curl -s http://localhost/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt)

if [ -n "$NGINX_RESPONSE" ]; then
    echo "✓ Nginx proxy works"
    echo "Response: $NGINX_RESPONSE"
else
    echo "✗ Nginx proxy does not work"
fi

echo ""
echo "3. Checking if response matches file content..."
FILE_CONTENT=$(cat api/static/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt)

if [ "$NGINX_RESPONSE" = "$FILE_CONTENT" ]; then
    echo "✓ Content matches perfectly"
else
    echo "✗ Content mismatch"
    echo "Expected: $FILE_CONTENT"
    echo "Got: $NGINX_RESPONSE"
fi

echo ""
echo "================================================"
echo "SSL Validation Endpoint Test Complete"
echo "================================================"
echo ""
echo "The endpoint is accessible at:"
echo "  http://35.192.6.155/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt"
echo ""
echo "To test from your server, run:"
echo "  curl http://35.192.6.155/.well-known/pki-validation/29EBA45A209B442CDB584C17035B3780.txt"
