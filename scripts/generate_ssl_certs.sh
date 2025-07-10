#!/bin/bash

# Generate SSL certificates for local development
# This script creates self-signed certificates for testing purposes

echo "🔐 Generating SSL certificates for local development..."

# Create nginx/ssl directory
mkdir -p nginx/ssl

# Generate private key
openssl genrsa -out nginx/ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key nginx/ssl/key.pem -out nginx/ssl/cert.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in nginx/ssl/cert.csr -signkey nginx/ssl/key.pem -out nginx/ssl/cert.pem

# Clean up CSR file
rm nginx/ssl/cert.csr

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificates saved in: nginx/ssl/"
echo "⚠️  These are self-signed certificates for development only"
echo "🔒 For production, use certificates from a trusted CA"

# Set proper permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

echo "🔧 Certificate permissions set correctly" 