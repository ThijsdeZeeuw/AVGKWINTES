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
    """Pydantic model for environment settings"""
    # Domain settings
    domain_name: str
    subdomain: str
    letsencrypt_email: str

    # Service ports
    n8n_port: int = 8000
    flowise_port: int = 3001
    webui_port: int = 3000
    supabase_port: int = 8000
    ollama_port: int = 11434
    searxng_port: int = 8080
    prometheus_port: int = 9090
    grafana_port: int = 3000
    whisper_port: int = 9000
    qdrant_port: int = 6333

    # Required secrets
    N8N_ENCRYPTION_KEY: str
    N8N_USER_MANAGEMENT_JWT_SECRET: str
    POSTGRES_PASSWORD: str
    JWT_SECRET: str
    ANON_KEY: str
    SERVICE_ROLE_KEY: str
    DASHBOARD_PASSWORD: str
    SECRET_KEY_BASE: str
    VAULT_ENC_KEY: str
    LOGFLARE_API_KEY: str
    GRAFANA_ADMIN_PASSWORD: str
    FLOWISE_PASSWORD: str

    class Config:
        env_file = ".env"

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

def setup_environment(settings: EnvironmentSettings, secrets_dict: Dict[str, str]):
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
        save_secrets(secrets_dict)
        
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

N8N_HOSTNAME=n8n.{DOMAIN_NAME}
WEBUI_HOSTNAME=openwebui.{DOMAIN_NAME}
FLOWISE_HOSTNAME=flowise.{DOMAIN_NAME}
SUPABASE_HOSTNAME=supabase.{DOMAIN_NAME}
OLLAMA_HOSTNAME=ollama.{DOMAIN_NAME}
SEARXNG_HOSTNAME=searxng.{DOMAIN_NAME}
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

SITE_URL=https://supabase.{DOMAIN_NAME}
ADDITIONAL_REDIRECT_URLS=
JWT_EXPIRY=3600
DISABLE_SIGNUP=false
API_EXTERNAL_URL=https://supabase.{DOMAIN_NAME}

## Mailer Config
MAILER_URLPATHS_CONFIRMATION=/auth/v1/verify
MAILER_URLPATHS_INVITE=/auth/v1/verify
MAILER_URLPATHS_RECOVERY=/auth/v1/verify
MAILER_URLPATHS_EMAIL_CHANGE=/auth/v1/verify

## Email auth
ENABLE_EMAIL_SIGNUP=false
ENABLE_EMAIL_AUTOCONFIRM=false
SMTP_ADMIN_EMAIL=admin@{DOMAIN_NAME}
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
SUPABASE_PUBLIC_URL=https://supabase.{DOMAIN_NAME}
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

DOMAIN_NAME={DOMAIN_NAME}
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

N8N_PORT={N8N_PORT}
FLOWISE_PORT={FLOWISE_PORT}
WEBUI_PORT={WEBUI_PORT}
SUPABASE_PORT={SUPABASE_PORT}
OLLAMA_PORT={OLLAMA_PORT}
SEARXNG_PORT={SEARXNG_PORT}
PROMETHEUS_PORT={PROMETHEUS_PORT}
GRAFANA_PORT={GRAFANA_PORT}
WHISPER_PORT={WHISPER_PORT}
QDRANT_PORT={QDRANT_PORT}

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
        logger.info("Docker is installed and running")
        return True
    except Exception as e:
        logger.error(f"Docker is not installed or not running: {str(e)}")
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
            logger.info(f"Port {port} is available")
        except Exception as e:
            logger.error(f"Port {port} is not available: {str(e)}")
            return False
    return True

def start_services() -> bool:
    """Start all services using docker-compose."""
    try:
        # Check Docker installation
        if not check_docker_installation():
            logger.error("Docker is not running. Please start Docker and try again.")
            return False
        
        # Check required ports
        if not check_required_ports():
            logger.error("Some required ports are not available. Please free up the ports and try again.")
            return False
        
        # Start services using docker-compose
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        logger.info("Services started successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error starting services: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Start Local AI Stack Services')
    parser.add_argument('--domain', default='kwintes.cloud', help='Domain name')
    parser.add_argument('--subdomain', default='n8n', help='Subdomain')
    parser.add_argument('--email', default='tddezeeuw@gmail.com', help='Email for Let\'s Encrypt')
    args = parser.parse_args()

    try:
        # Create settings object
        settings = EnvironmentSettings(
            domain_name=args.domain,
            subdomain=args.subdomain,
            letsencrypt_email=args.email
        )
        
        # Generate secrets
        secrets_dict = generate_secrets()
        
        # Setup environment
        setup_environment(settings, secrets_dict)
        
        # Check prerequisites
        if not check_docker_installation():
            logger.error("Docker is not properly installed or running")
            sys.exit(1)
            
        if not check_required_ports():
            logger.error("Required ports are not available")
            sys.exit(1)
        
        # Start services
        if not start_services():
            logger.error("Failed to start services")
            sys.exit(1)
            
        logger.info("Setup completed successfully!")
        logger.info("You can access the services at:")
        logger.info("- n8n: https://n8n.{DOMAIN_NAME}")
        logger.info("- Flowise: https://flowise.{DOMAIN_NAME}")
        logger.info("- WebUI: https://openwebui.{DOMAIN_NAME}")
        logger.info("- Supabase: https://supabase.{DOMAIN_NAME}")
        logger.info("- Ollama: https://ollama.{DOMAIN_NAME}")
        logger.info("- SearXNG: https://searxng.{DOMAIN_NAME}")
        logger.info("- Grafana: https://grafana.{DOMAIN_NAME}")
        logger.info("- Prometheus: https://prometheus.{DOMAIN_NAME}")
        logger.info("- Whisper: https://whisper.{DOMAIN_NAME}")
        logger.info("- Qdrant: https://qdrant.{DOMAIN_NAME}")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Created and maintained by Z4Y