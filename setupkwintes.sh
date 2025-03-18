#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if command_exists netstat; then
        netstat -tuln | grep ":$port " >/dev/null 2>&1
    else
        lsof -i :$port >/dev/null 2>&1
    fi
}

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        echo "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if Python is installed
check_python() {
    if ! command_exists python3; then
        echo "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
}

# Function to check if pip is installed
check_pip() {
    if ! command_exists pip3; then
        echo "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
}

# Function to check if virtualenv is installed
check_virtualenv() {
    if ! command_exists virtualenv; then
        echo "virtualenv is not installed. Installing..."
        pip3 install virtualenv
    fi
}

# Function to check if required ports are available
check_ports() {
    local ports=(8000 3000 3001 11434 8080 9090 9000 6333)
    for port in "${ports[@]}"; do
        if check_port "$port"; then
            echo "Port $port is already in use. Please free up the port and try again."
            exit 1
        fi
    done
}

# Function to create and activate virtual environment
setup_virtualenv() {
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
}

# Function to install required Python packages
install_requirements() {
    echo "Installing required Python packages..."
    pip install docker python-dotenv pydantic requests aiohttp fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] email-validator pydantic-settings
}

# Function to create data directories
create_data_dirs() {
    echo "Creating data directories..."
    mkdir -p data/{n8n,flowise,webui,supabase,ollama,searxng,prometheus,grafana,whisper,qdrant}
    chmod -R 755 data
}

# Function to run the setup script
run_setup() {
    echo "Running setup script..."
    python start_services.py --domain kwintes.cloud --subdomain n8n --email tddezeeuw@gmail.com
}

# Main setup process
echo "Starting Kwintes setup..."

# Check prerequisites
check_docker
check_python
check_pip
check_virtualenv
check_ports

# Setup environment
setup_virtualenv
install_requirements
create_data_dirs

# Run setup script
run_setup

echo "Setup completed!"
echo "You can access the services at:"
echo "- n8n: https://n8n.kwintes.cloud"
echo "- Flowise: https://flowise.kwintes.cloud"
echo "- WebUI: https://openwebui.kwintes.cloud"
echo "- Supabase: https://supabase.kwintes.cloud"
echo "- Ollama: https://ollama.kwintes.cloud"
echo "- SearXNG: https://searxng.kwintes.cloud"
echo "- Grafana: https://grafana.kwintes.cloud"
echo "- Prometheus: https://prometheus.kwintes.cloud"
echo "- Whisper: https://whisper.kwintes.cloud"
echo "- Qdrant: https://qdrant.kwintes.cloud" 