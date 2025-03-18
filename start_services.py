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
    secrets = {
        'N8N_ENCRYPTION_KEY': generate_random_string(32),
        'N8N_USER_MANAGEMENT_JWT_SECRET': generate_random_string(32),
        'POSTGRES_PASSWORD': generate_random_string(32),
        'JWT_SECRET': generate_random_string(32),
        'ANON_KEY': generate_random_string(32),
        'SERVICE_ROLE_KEY': generate_random_string(32),
        'DASHBOARD_PASSWORD': generate_random_string(32),
        'SECRET_KEY_BASE': generate_random_string(64),
        'VAULT_ENC_KEY': generate_random_string(32),
        'LOGFLARE_API_KEY': generate_random_string(32),
        'GRAFANA_ADMIN_PASSWORD': generate_random_string(32),
        'FLOWISE_PASSWORD': generate_random_string(32)
    }
    return secrets

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

def setup_environment(settings: EnvironmentSettings, secrets_dict: Dict[str, str]) -> bool:
    """Set up the environment with required configurations."""
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
        
        # Create .env file with all required settings
        env_content = f"""# Caddy Config
DOMAIN_NAME={settings.domain_name}
LETSENCRYPT_EMAIL={settings.letsencrypt_email}

# Database Configuration
POSTGRES_PASSWORD={secrets_dict['POSTGRES_PASSWORD']}
POSTGRES_USER=postgres
POSTGRES_DB=postgres

# Supavisor Configuration
SUPAVISOR_DB_URL=postgresql://postgres:{secrets_dict['POSTGRES_PASSWORD']}@db:5432/postgres
SUPAVISOR_JWT_SECRET={secrets_dict['JWT_SECRET']}
SUPAVISOR_ANON_KEY={secrets_dict['ANON_KEY']}
SUPAVISOR_SERVICE_ROLE_KEY={secrets_dict['SERVICE_ROLE_KEY']}

# API Proxy Configuration
API_PROXY_SECRET={secrets_dict['SECRET_KEY_BASE']}
API_PROXY_VAULT_KEY={secrets_dict['VAULT_ENC_KEY']}

# Logging Configuration
LOGFLARE_API_KEY={secrets_dict['LOGFLARE_API_KEY']}

# Monitoring Configuration
GRAFANA_ADMIN_PASSWORD={secrets_dict['GRAFANA_ADMIN_PASSWORD']}

# N8N Configuration
N8N_ENCRYPTION_KEY={secrets_dict['N8N_ENCRYPTION_KEY']}
N8N_USER_MANAGEMENT_JWT_SECRET={secrets_dict['N8N_USER_MANAGEMENT_JWT_SECRET']}

# Flowise Configuration
FLOWISE_PASSWORD={secrets_dict['FLOWISE_PASSWORD']}

# Service Ports
N8N_PORT={settings.n8n_port}
FLOWISE_PORT={settings.flowise_port}
WEBUI_PORT={settings.webui_port}
SUPABASE_PORT={settings.supabase_port}
OLLAMA_PORT={settings.ollama_port}
SEARXNG_PORT={settings.searxng_port}
PROMETHEUS_PORT={settings.prometheus_port}
GRAFANA_PORT={settings.grafana_port}
WHISPER_PORT={settings.whisper_port}
QDRANT_PORT={settings.qdrant_port}
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        logging.info("Environment configuration completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Failed to set up environment: {str(e)}")
        return False

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

def start_services(settings: EnvironmentSettings) -> bool:
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
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Start local AI services')
    parser.add_argument('--domain', required=True, help='Domain name for the services')
    parser.add_argument('--subdomain', required=True, help='Subdomain for the services')
    parser.add_argument('--email', required=True, help='Email for Let\'s Encrypt')
    args = parser.parse_args()

    # Generate secrets
    secrets_dict = generate_secrets()
    
    # Create settings object
    settings = EnvironmentSettings(
        domain_name=args.domain,
        subdomain=args.subdomain,
        letsencrypt_email=args.email,
        **secrets_dict  # Add all secrets to settings
    )

    try:
        # Set up environment
        if not setup_environment(settings, secrets_dict):
            logging.error("Environment setup failed")
            return False

        # Start services
        if not start_services(settings):
            logging.error("Failed to start services")
            return False

        logging.info("All services started successfully")
        return True

    except Exception as e:
        logging.error(f"Setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()

# Created and maintained by Z4Y