#!/usr/bin/env python3
"""
start_services.py

This script starts the Supabase stack first, waits for it to initialize, and then starts
the local AI stack. Both stacks use the same Docker Compose project name ("localai")
so they appear together in Docker Desktop.
"""

import os
import subprocess
import shutil
import time
import argparse
import platform
import sys
import secrets
import string
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import docker
from dotenv import load_dotenv
import pydantic
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnvironmentSettings(BaseSettings):
    """Pydantic model for environment settings."""
    N8N_ENCRYPTION_KEY: str
    N8N_USER_MANAGEMENT_JWT_SECRET: str
    POSTGRES_PASSWORD: str
    JWT_SECRET: str
    ANON_KEY: str
    SERVICE_ROLE_KEY: str
    DASHBOARD_USERNAME: str = "admin"
    DASHBOARD_PASSWORD: str
    POOLER_TENANT_ID: int = 1001
    DOMAIN_NAME: str = "kwintes.cloud"
    LETSENCRYPT_EMAIL: str = "tddezeeuw@gmail.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def generate_random_string(length: int = 32) -> str:
    """Generate a random string of specified length."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secrets() -> Dict[str, str]:
    """Generate all required secrets."""
    return {
        'N8N_ENCRYPTION_KEY': generate_random_string(32),
        'N8N_USER_MANAGEMENT_JWT_SECRET': generate_random_string(32),
        'POSTGRES_PASSWORD': generate_random_string(16),
        'JWT_SECRET': generate_random_string(32),
        'ANON_KEY': generate_random_string(32),
        'SERVICE_ROLE_KEY': generate_random_string(32),
        'DASHBOARD_PASSWORD': generate_random_string(16),
        'SECRET_KEY_BASE': generate_random_string(32),
        'VAULT_ENC_KEY': generate_random_string(32),
        'LOGFLARE_API_KEY': generate_random_string(32),
        'GRAFANA_ADMIN_PASSWORD': generate_random_string(16),
        'FLOWISE_PASSWORD': generate_random_string(16)
    }

def save_secrets(secrets_dict: Dict[str, str], secrets_file: str = 'secrets.txt'):
    """Save generated secrets to a file."""
    try:
        with open(secrets_file, 'w') as f:
            f.write("# Generated Secrets for Kwintes Setup\n")
            f.write("# Created and maintained by Z4Y\n")
            f.write(f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key, value in secrets_dict.items():
                f.write(f"{key}={value}\n")
            
            f.write("\n# Domain Information\n")
            f.write("DOMAIN=kwintes.cloud\n")
            f.write("SUBDOMAINS:\n")
            subdomains = [
                'n8n', 'openwebui', 'flowise', 'supabase', 'ollama',
                'searxng', 'grafana', 'prometheus', 'whisper', 'qdrant'
            ]
            for subdomain in subdomains:
                f.write(f"- {subdomain}.kwintes.cloud\n")
            
            f.write("\n# Service Ports\n")
            ports = {
                'N8N_PORT': 8000,
                'FLOWISE_PORT': 3001,
                'WEBUI_PORT': 3000,
                'SUPABASE_PORT': 8000,
                'OLLAMA_PORT': 11434,
                'SEARXNG_PORT': 8080,
                'PROMETHEUS_PORT': 9090,
                'GRAFANA_PORT': 3000,
                'WHISPER_PORT': 9000,
                'QDRANT_PORT': 6333
            }
            for port_name, port_value in ports.items():
                f.write(f"{port_name}={port_value}\n")
            
            f.write("\n# Important Notes:\n")
            f.write("# 1. Keep this file secure and never commit it to version control\n")
            f.write("# 2. Backup this file in a secure location\n")
            f.write("# 3. These secrets are used to generate the .env file\n")
            f.write("# 4. For production, change all passwords and keys\n")
            f.write("# 5. Update SMTP credentials when configuring email\n")
        
        logger.info(f"Secrets saved to {secrets_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving secrets: {str(e)}")
        return False

def setup_environment(interactive: bool = True) -> None:
    """Set up the environment with all necessary configurations."""
    try:
        # Create data directories
        data_dirs = [
            'data/n8n',
            'data/flowise',
            'data/webui',
            'data/supabase',
            'data/ollama',
            'data/searxng',
            'data/prometheus',
            'data/grafana',
            'data/whisper',
            'data/qdrant'
        ]
        
        for dir_path in data_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            os.chmod(dir_path, 0o755)
        
        # Generate and save secrets
        secrets_dict = generate_secrets()
        if not save_secrets(secrets_dict):
            raise Exception("Failed to save secrets")
        
        # Create .env file with all configurations
        env_content = """############
# [required] 
# n8n credentials
############

N8N_ENCRYPTION_KEY={N8N_ENCRYPTION_KEY}
N8N_USER_MANAGEMENT_JWT_SECRET={N8N_USER_MANAGEMENT_JWT_SECRET}

############
# [required] 
# Supabase Secrets
############

POSTGRES_PASSWORD={POSTGRES_PASSWORD}
JWT_SECRET={JWT_SECRET}
ANON_KEY={ANON_KEY}
SERVICE_ROLE_KEY={SERVICE_ROLE_KEY}
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD={DASHBOARD_PASSWORD}
POOLER_TENANT_ID=1001

############
# [required for prod] 
# Caddy Config
############

N8N_HOSTNAME=n8n.kwintes.cloud
WEBUI_HOSTNAME=openwebui.kwintes.cloud
FLOWISE_HOSTNAME=flowise.kwintes.cloud
SUPABASE_HOSTNAME=supabase.kwintes.cloud
OLLAMA_HOSTNAME=ollama.kwintes.cloud
SEARXNG_HOSTNAME=searxng.kwintes.cloud
LETSENCRYPT_EMAIL={LETSENCRYPT_EMAIL}

############
# Database Configuration
############

POSTGRES_HOST=db
POSTGRES_DB=postgres
POSTGRES_PORT=5432

############
# Supavisor Configuration
############

POOLER_PROXY_PORT_TRANSACTION=5432
POOLER_DEFAULT_POOL_SIZE=15
POOLER_MAX_CLIENT_CONN=100
SECRET_KEY_BASE={SECRET_KEY_BASE}
VAULT_ENC_KEY={VAULT_ENC_KEY}

############
# API Proxy Configuration
############

KONG_HTTP_PORT=8000
KONG_HTTPS_PORT=8443

############
# API Configuration
############

PGRST_DB_SCHEMAS=public,storage

############
# Auth Configuration
############

SITE_URL=https://supabase.kwintes.cloud
ADDITIONAL_REDIRECT_URLS=
JWT_EXPIRY=3600
DISABLE_SIGNUP=false
API_EXTERNAL_URL=https://supabase.kwintes.cloud

## Mailer Config
MAILER_URLPATHS_CONFIRMATION=/auth/v1/verify
MAILER_URLPATHS_INVITE=/auth/v1/verify
MAILER_URLPATHS_RECOVERY=/auth/v1/verify
MAILER_URLPATHS_EMAIL_CHANGE=/auth/v1/verify

## Email auth
ENABLE_EMAIL_SIGNUP=false
ENABLE_EMAIL_AUTOCONFIRM=false
SMTP_ADMIN_EMAIL=admin@kwintes.cloud
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
SMTP_SENDER_NAME=Kwintes
ENABLE_ANONYMOUS_USERS=false

## Phone auth
ENABLE_PHONE_SIGNUP=false
ENABLE_PHONE_AUTOCONFIRM=false

############
# Studio Configuration
############

STUDIO_DEFAULT_ORGANIZATION=Default Organization
STUDIO_DEFAULT_PROJECT=Default Project
STUDIO_PORT=3000
SUPABASE_PUBLIC_URL=https://supabase.kwintes.cloud
IMGPROXY_ENABLE_WEBP_DETECTION=true
OPENAI_API_KEY=

############
# Functions Configuration
############

FUNCTIONS_VERIFY_JWT=true

############
# Logs Configuration
############

LOGFLARE_API_KEY={LOGFLARE_API_KEY}
DOCKER_SOCKET_LOCATION=/var/run/docker.sock

############
# Domain Settings
############

DOMAIN_NAME=kwintes.cloud
SUBDOMAIN=n8n

############
# Grafana Configuration
############

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD={GRAFANA_ADMIN_PASSWORD}
DATA_FOLDER=./data

############
# Flowise Configuration
############

FLOWISE_USERNAME=admin
FLOWISE_PASSWORD={FLOWISE_PASSWORD}
ENABLE_METRICS=true
METRICS_PROVIDER=prometheus
METRICS_INCLUDE_NODE_METRICS=true

############
# Service Ports
############

N8N_PORT=8000
FLOWISE_PORT=3001
WEBUI_PORT=3000
SUPABASE_PORT=8000
OLLAMA_PORT=11434
SEARXNG_PORT=8080
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
WHISPER_PORT=9000
QDRANT_PORT=6333

# Created and maintained by Z4Y
"""
        
        # Write the .env file with the generated secrets
        with open('.env', 'w') as f:
            f.write(env_content.format(**secrets_dict))
        
        logger.info("Environment setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during environment setup: {str(e)}")
        raise

def check_docker_installation() -> bool:
    """Check if Docker is installed and running."""
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception as e:
        logger.error(f"Docker check failed: {str(e)}")
        return False

def check_required_ports() -> bool:
    """Check if required ports are available."""
    required_ports = [8000, 3000, 3001, 11434, 8080, 9090, 9000, 6333]
    for port in required_ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
        except Exception as e:
            logger.error(f"Port {port} is not available: {str(e)}")
            return False
    return True

def start_services() -> None:
    """Start all services using docker-compose."""
    try:
        # Check Docker installation
        if not check_docker_installation():
            logger.error("Docker is not running. Please start Docker and try again.")
            return
        
        # Check required ports
        if not check_required_ports():
            logger.error("Some required ports are not available. Please free up the ports and try again.")
            return
        
        # Start services using docker-compose
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        logger.info("Services started successfully")
        
    except Exception as e:
        logger.error(f"Error starting services: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Start Local AI Stack Services')
    parser.add_argument('--interactive', action='store_true', default=True,
                      help='Run in interactive mode (default: True)')
    args = parser.parse_args()
    
    try:
        # Set up environment
        setup_environment(args.interactive)
        
        # Start services
        start_services()
        
        logger.info("Setup completed successfully!")
        logger.info("You can access the services at:")
        logger.info("- n8n: https://n8n.kwintes.cloud")
        logger.info("- Flowise: https://flowise.kwintes.cloud")
        logger.info("- WebUI: https://openwebui.kwintes.cloud")
        logger.info("- Supabase: https://supabase.kwintes.cloud")
        logger.info("- Ollama: https://ollama.kwintes.cloud")
        logger.info("- SearXNG: https://searxng.kwintes.cloud")
        logger.info("- Grafana: https://grafana.kwintes.cloud")
        logger.info("- Prometheus: https://prometheus.kwintes.cloud")
        logger.info("- Whisper: https://whisper.kwintes.cloud")
        logger.info("- Qdrant: https://qdrant.kwintes.cloud")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Created and maintained by Z4Y