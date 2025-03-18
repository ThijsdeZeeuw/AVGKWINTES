# Local AI Stack for Kwintes

A comprehensive local AI stack deployment for Kwintes, featuring multiple AI models, workflow automation, and secure document processing capabilities.

# Created and maintained by Z4Y

## Features

- **Local AI Processing**: All AI operations run locally on your infrastructure
- **Multi-Model Support**: Access to various LLMs and embedding models
- **Workflow Automation**: n8n and Flowise integration
- **Secure Document Processing**: Built-in security features for sensitive data
- **Monitoring & Analytics**: Prometheus and Grafana integration
- **Search Capabilities**: Integrated SearXNG for efficient document search
- **Multi-Language Support**: Advanced language processing capabilities
- **API Integration**: RESTful API endpoints for all services

## Prerequisites

### Server Requirements
- Ubuntu 22.04 LTS or newer
- Minimum 16GB RAM
- 100GB+ storage
- Domain name with DNS access

### Required Subdomains
- n8n.kwintes.cloud
- openwebui.kwintes.cloud
- flowise.kwintes.cloud
- supabase.kwintes.cloud
- ollama.kwintes.cloud
- searxng.kwintes.cloud
- grafana.kwintes.cloud
- prometheus.kwintes.cloud
- whisper.kwintes.cloud
- qdrant.kwintes.cloud

## Installation

### 1. System Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    git \
    build-essential \
    software-properties-common \
    nginx \
    certbot \
    python3-certbot-nginx
```

### 2. Python Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip in the virtual environment
python -m pip install --upgrade pip

# Install required Python packages
pip install \
    docker \
    python-dotenv \
    pydantic \
    requests \
    aiohttp \
    fastapi \
    uvicorn \
    python-multipart \
    python-jose[cryptography] \
    passlib[bcrypt] \
    email-validator \
    pydantic-settings
```

### 3. Docker Installation
```bash
# Remove old Docker installations
sudo apt remove -y docker docker-engine docker.io containerd runc

# Install Docker prerequisites
sudo apt update
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
```

### 4. Repository Setup
```bash
# Clone repository
git clone https://github.com/ThijsdeZeeuw/AVGKWINTES.git
cd AVGKWINTES

# Create data directories
mkdir -p data/{n8n,flowise,webui,supabase,ollama,searxng,prometheus,grafana,whisper,qdrant}
chmod -R 755 data
```

### 5. Environment Configuration
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Generate secrets
./generate_secrets.sh

# Run interactive setup script
python start_services.py --interactive
```

### 6. Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

## Available AI Models

### Large Language Models (LLMs)
1. gemma3:12b
   - Source: Google
   - Description: 12B parameter model with strong reasoning capabilities

2. granite3-guardian:8b
   - Source: IBM
   - Description: 8B parameter model with enhanced security features

3. llama2:13b
   - Source: Meta
   - Description: 13B parameter model with strong general capabilities

4. llama2:7b
   - Source: Meta
   - Description: 7B parameter model optimized for efficiency

5. mistral:7b
   - Source: Mistral AI
   - Description: 7B parameter model with excellent performance

6. mistral:7b-instruct
   - Source: Mistral AI
   - Description: Instruction-tuned version of Mistral 7B

7. mistral:7b-openorca
   - Source: Mistral AI
   - Description: OpenOrca fine-tuned version of Mistral 7B

8. mistral:7b-solar
   - Source: Mistral AI
   - Description: Solar fine-tuned version of Mistral 7B

9. mistral:7b-solar-instruct
   - Source: Mistral AI
   - Description: Instruction-tuned version of Mistral 7B Solar

10. mistral:7b-solar-openorca
    - Source: Mistral AI
    - Description: OpenOrca fine-tuned version of Mistral 7B Solar

11. mistral:7b-solar-openorca-instruct
    - Source: Mistral AI
    - Description: Instruction-tuned version of Mistral 7B Solar OpenOrca

12. mistral:7b-solar-openorca-instruct-v2
    - Source: Mistral AI
    - Description: V2 version of the instruction-tuned Mistral 7B Solar OpenOrca

13. mistral:7b-solar-openorca-instruct-v2.1
    - Source: Mistral AI
    - Description: V2.1 version of the instruction-tuned Mistral 7B Solar OpenOrca

### Embedding Models
1. granite-embedding:278m
   - Source: IBM
   - Description: 278M parameter model optimized for text embeddings

2. mistral-embedding:7b
   - Source: Mistral AI
   - Description: 7B parameter model for high-quality text embeddings

## Security Features

1. **Local Processing**
   - All AI operations run on your infrastructure
   - No data leaves your network
   - Complete control over data flow

2. **Secure Infrastructure**
   - HTTPS encryption for all services
   - Firewall protection
   - Regular security updates
   - Access control and authentication

3. **Data Protection**
   - Encrypted storage
   - Secure secret management
   - Regular backups
   - Audit logging

4. **Access Control**
   - Role-based access control
   - Multi-factor authentication
   - Session management
   - IP whitelisting

## Maintenance

### Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Update Python dependencies (in virtual environment)
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Backup Procedures
```bash
# Backup data directories
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Backup environment files
cp .env .env.backup
cp secrets.txt secrets.txt.backup
```

### Monitoring
```bash
# Check service logs
docker-compose logs -f

# Monitor system resources
htop
```

## Support

For support or issues:
1. Check the logs: `docker-compose logs -f`
2. Verify service status: `docker-compose ps`
3. Check system resources: `htop`
4. Review security logs: `journalctl -u docker`

## License

This project is proprietary and confidential. All rights reserved.

# Created and maintained by Z4Y
