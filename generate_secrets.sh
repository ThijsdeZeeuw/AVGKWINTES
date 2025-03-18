#!/bin/bash

# Generate Secrets for Kwintes Setup
# Created and maintained by Z4Y

# Function to generate a random hex string
generate_hex() {
    local length=$1
    openssl rand -hex "$length"
}

# Create .env file with secure secrets
cat > .env << EOL
# N8N Configuration
N8N_HOSTNAME=n8n.kwintes.cloud
N8N_PROTOCOL=https
N8N_PORT=8000
N8N_EDITOR_BASE_URL=https://n8n.kwintes.cloud
N8N_ENCRYPTION_KEY=$(generate_hex 32)
N8N_USER_MANAGEMENT_JWT_SECRET=$(generate_hex 32)

# Database Configuration
POSTGRES_PASSWORD=$(generate_hex 16)

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=$(generate_hex 16)

# Whisper Configuration
ASR_MODEL=base
ASR_ENGINE=openai_whisper
ASR_DEVICE=cpu
MODEL_IDLE_TIMEOUT=3600

# Domain Configuration
DOMAIN=kwintes.cloud
SUBDOMAIN=n8n
EMAIL=tddezeeuw@gmail.com
EOL

# Make the .env file readable only by the owner
chmod 600 .env

echo "Generated secure secrets and created .env file"

# Created and maintained by Z4Y 