# Local AI Stack for Kwintes

A comprehensive local AI stack deployment for Kwintes, featuring multiple AI models and services.

# Created and maintained by Z4Y

## Features

- **Multiple AI Models**: Support for various LLMs and embedding models
- **Secure Infrastructure**: All services run locally with proper security measures
- **Easy Setup**: Interactive setup process with automatic configuration
- **Monitoring**: Built-in monitoring with Prometheus and Grafana
- **Document Processing**: Support for text and vision-based document analysis
- **Multi-language Support**: Handle documents in multiple languages
- **API Access**: RESTful APIs for all services
- **Web Interface**: User-friendly web interfaces for all components

## Prerequisites

### System Requirements
- Ubuntu 22.04 LTS or newer
- Minimum 16GB RAM
- 100GB+ storage
- Domain name with DNS access

### Required Software
- Docker and Docker Compose
- Python 3.8 or newer
- Git
- UFW (Uncomplicated Firewall)

## Installation Steps

### 1. System Update and Basic Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install basic requirements
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    git \
    ufw \
    nano \
    htop \
    net-tools \
    wget \
    unzip \
    build-essential \
    python3-dev
```

### 2. Install Python Dependencies
```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Install required Python packages
pip3 install \
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
    python-jose[cryptography] \
    python-multipart \
    email-validator \
    pydantic-settings
```

### 3. Install Docker
```bash
# Remove old versions
sudo apt remove -y docker docker-engine docker.io containerd runc
sudo apt autoremove -y

# Install Docker prerequisites
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
```

### 4. Configure Firewall
```bash
# Enable UFW
sudo ufw enable

# Allow SSH (important!)
sudo ufw allow 22/tcp

# Allow required ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 3001/tcp
sudo ufw allow 11434/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 9090/tcp
sudo ufw allow 9000/tcp
sudo ufw allow 6333/tcp

# Verify firewall status
sudo ufw status
```

### 5. Create Required Directories
```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone repository
git clone https://github.com/ThijsdeZeeuw/AVGKWINTES.git
cd AVGKWINTES

# Create data directories
mkdir -p data/{n8n,flowise,webui,supabase,ollama,searxng,prometheus,grafana,whisper,qdrant}

# Set proper permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

### 6. Environment Setup
```bash
# Make scripts executable
chmod +x generate_secrets.sh apply_secrets.sh

# Generate secrets
./generate_secrets.sh

# Apply secrets to .env file
./apply_secrets.sh

# Run the interactive setup
python3 start_services.py --interactive
```

### 7. Start Services
```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check service logs if needed
docker-compose logs -f [service_name]
```

### 8. Verify Installation
```bash
# Check running containers
docker ps

# Verify services are accessible
curl https://n8n.kwintes.cloud/healthz  # n8n
curl https://qdrant.kwintes.cloud/healthz  # Qdrant
curl https://prometheus.kwintes.cloud/-/healthy  # Prometheus
```

## Installed Components

### 1. n8n Workflows
- **Document Analysis Flow**
  - Input: Document text/image
  - Processing: Text extraction, sentiment analysis, entity recognition
  - Output: Structured analysis report
  - Models used: gemma3:12b, granite3-guardian:8b

- **Client Report Generation**
  - Input: Session notes, client history
  - Processing: Text summarization, risk assessment
  - Output: Formatted client report
  - Models used: granite3-guardian:8b-instruct

- **Multi-language Processing**
  - Input: Multi-language documents
  - Processing: Translation, sentiment analysis
  - Output: Translated and analyzed content
  - Models used: granite-embedding:278m

### 2. Supabase Integration
- **Database Tables**
  - clients: Client information and history
  - documents: Document storage and metadata
  - reports: Generated reports and analysis
  - users: System users and permissions

- **API Endpoints**
  - /api/v1/clients: Client management
  - /api/v1/documents: Document processing
  - /api/v1/reports: Report generation
  - /api/v1/analysis: Document analysis

### 3. Qdrant Vector Store
- **Collections**
  - documents: Document embeddings
  - reports: Report embeddings
  - clients: Client information embeddings

- **Search Capabilities**
  - Semantic search
  - Similarity matching
  - Hybrid search (keyword + semantic)

### 4. Monitoring Stack
- **Prometheus Metrics**
  - Service health
  - Resource usage
  - API latency
  - Error rates
  - Model performance

- **Grafana Dashboards**
  - System overview
  - Service metrics
  - Model performance
  - Error tracking
  - Resource utilization

## Available AI Models

### Large Language Models (LLMs)

#### 1. gemma3:12b
- **Source**: Google
- **Size**: 12B parameters
- **Use Cases**:
  - General text understanding
  - Document analysis
  - Text generation
  - Question answering
- **Features**:
  - Multilingual support
  - Code understanding
  - Reasoning capabilities
  - Context window: 8K tokens

#### 2. granite3-guardian:8b
- **Source**: IBM
- **Size**: 8B parameters
- **Use Cases**:
  - Safe text generation
  - Ethical AI interactions
  - Content moderation
  - Risk assessment
- **Features**:
  - Built-in safety filters
  - Ethical guidelines
  - Bias detection
  - Context window: 4K tokens

#### 3. granite3-guardian:8b-instruct
- **Source**: IBM
- **Size**: 8B parameters
- **Use Cases**:
  - Instruction following
  - Task completion
  - Process automation
  - Workflow guidance
- **Features**:
  - Step-by-step reasoning
  - Task decomposition
  - Error handling
  - Context window: 4K tokens

#### 4. granite3-guardian:8b-q4_K_M
- **Source**: IBM
- **Size**: 8B parameters (quantized)
- **Use Cases**:
  - Efficient inference
  - Resource-constrained environments
  - Batch processing
  - Real-time applications
- **Features**:
  - 4-bit quantization
  - Reduced memory usage
  - Faster inference
  - Context window: 4K tokens

[Additional LLM models follow the same detailed format...]

### Embedding Models

#### 1. granite-embedding:278m
- **Source**: IBM
- **Size**: 278M parameters
- **Use Cases**:
  - Text embedding
  - Semantic search
  - Document similarity
  - Clustering
- **Features**:
  - Multilingual support
  - Fast inference
  - High accuracy
  - Efficient storage

#### 2. granite-embedding:278m-v2
- **Source**: IBM
- **Size**: 278M parameters
- **Use Cases**:
  - Enhanced text embedding
  - Improved semantic search
  - Better document similarity
  - Advanced clustering
- **Features**:
  - Improved multilingual support
  - Enhanced accuracy
  - Better performance
  - Optimized storage

## Security Features

1. **Local Deployment**: All processing happens on your infrastructure
2. **Secure Infrastructure**:
   - HTTPS encryption for all services
   - Firewall rules for port protection
   - Regular security updates
   - Secure secret management

3. **Access Control**:
   - Role-based access control
   - JWT authentication
   - API key management
   - User management

4. **Data Protection**:
   - Local data storage
   - Encrypted communication
   - Secure backup system
   - Data retention policies

## Local AI Capabilities

### Text Processing
- Document analysis
- Text classification
- Sentiment analysis
- Entity extraction
- Multi-language support
- Text summarization
- Question answering

### Vision Capabilities
- Document image analysis
- OCR processing
- Visual question answering
- Image classification
- Object detection
- Scene understanding

## GGZ/FBW Client Support

### Document Generation and Analysis
- Automated report generation
- Client history analysis
- Risk assessment support
- Treatment plan suggestions
- Progress tracking
- Compliance checking

### Client Understanding and Support
- Multi-language document processing
- Cultural context awareness
- Accessibility features
- Privacy-focused processing
- Secure data handling
- Client-specific customization

### Benefits for GGZ/FBW Organizations
1. **Efficiency**:
   - Automated document processing
   - Quick report generation
   - Streamlined workflows
   - Reduced manual work

2. **Quality**:
   - Consistent documentation
   - Standardized reports
   - Error reduction
   - Quality assurance

3. **Compliance**:
   - GDPR compliance
   - Data protection
   - Audit trails
   - Security standards

4. **Support**:
   - Multi-language support
   - Accessibility features
   - Cultural sensitivity
   - Client-specific needs

## Maintenance

### Regular Tasks
1. Monitor system resources
2. Check service logs
3. Update Docker images
4. Backup data
5. Review security logs
6. Update SSL certificates
7. Clean up old logs
8. Monitor disk space
9. Check service health
10. Update documentation

### Backup Procedure
1. Stop services
2. Backup data directories
3. Backup .env and secrets.txt
4. Backup Docker volumes
5. Verify backup integrity
6. Document backup date
7. Test restore procedure

## Support

For support or issues:
1. Check service logs
2. Review documentation
3. Contact system administrator
4. Check GitHub issues
5. Review security advisories

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Created and maintained by Z4Y
