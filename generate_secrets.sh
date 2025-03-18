#!/bin/bash

# Generate Secrets for Kwintes Setup
# Created and maintained by Z4Y

# Function to generate random string
generate_random_string() {
    local length=$1
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c "$length"
}

# Create secrets directory if it doesn't exist
mkdir -p secrets

# Generate secrets
echo "# Generated Secrets for Kwintes Setup" > secrets.txt
echo "# Created and maintained by Z4Y" >> secrets.txt
echo "# Generated on: $(date '+%Y-%m-%d %H:%M:%S')" >> secrets.txt
echo "" >> secrets.txt

# Generate and save secrets
{
    echo "N8N_ENCRYPTION_KEY=$(generate_random_string 32)"
    echo "N8N_USER_MANAGEMENT_JWT_SECRET=$(generate_random_string 32)"
    echo "POSTGRES_PASSWORD=$(generate_random_string 16)"
    echo "JWT_SECRET=$(generate_random_string 32)"
    echo "ANON_KEY=$(generate_random_string 32)"
    echo "SERVICE_ROLE_KEY=$(generate_random_string 32)"
    echo "DASHBOARD_PASSWORD=$(generate_random_string 16)"
    echo "SECRET_KEY_BASE=$(generate_random_string 32)"
    echo "VAULT_ENC_KEY=$(generate_random_string 32)"
    echo "LOGFLARE_API_KEY=$(generate_random_string 32)"
    echo "GRAFANA_ADMIN_PASSWORD=$(generate_random_string 16)"
    echo "FLOWISE_PASSWORD=$(generate_random_string 16)"
} >> secrets.txt

# Add domain information
echo "" >> secrets.txt
echo "# Domain Information" >> secrets.txt
echo "DOMAIN=kwintes.cloud" >> secrets.txt
echo "SUBDOMAINS:" >> secrets.txt
for subdomain in n8n openwebui flowise supabase ollama searxng grafana prometheus whisper qdrant; do
    echo "- ${subdomain}.kwintes.cloud" >> secrets.txt
done

# Add service ports
echo "" >> secrets.txt
echo "# Service Ports" >> secrets.txt
{
    echo "N8N_PORT=8000"
    echo "FLOWISE_PORT=3001"
    echo "WEBUI_PORT=3000"
    echo "SUPABASE_PORT=8000"
    echo "OLLAMA_PORT=11434"
    echo "SEARXNG_PORT=8080"
    echo "PROMETHEUS_PORT=9090"
    echo "GRAFANA_PORT=3000"
    echo "WHISPER_PORT=9000"
    echo "QDRANT_PORT=6333"
} >> secrets.txt

# Add important notes
echo "" >> secrets.txt
echo "# Important Notes:" >> secrets.txt
echo "# 1. Keep this file secure and never commit it to version control" >> secrets.txt
echo "# 2. Backup this file in a secure location" >> secrets.txt
echo "# 3. These secrets are used to generate the .env file" >> secrets.txt
echo "# 4. For production, change all passwords and keys" >> secrets.txt
echo "# 5. Update SMTP credentials when configuring email" >> secrets.txt

# Set proper permissions
chmod 600 secrets.txt

echo "Secrets have been generated and saved to secrets.txt"
echo "Please keep this file secure and never commit it to version control."

# Created and maintained by Z4Y 