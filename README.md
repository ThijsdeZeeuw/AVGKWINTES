# Local AI Stack

A comprehensive local AI stack deployment that includes various AI services and tools.

## Features

- **AI Models**: Access to various AI models through Ollama
- **Workflow Automation**: N8N for workflow automation
- **AI Development**: Flowise for AI development
- **Web Interface**: OpenWebUI for model interaction
- **Database**: Supabase for data storage
- **Search**: SearXNG for web search
- **Monitoring**: Prometheus and Grafana for system monitoring
- **Speech Processing**: Whisper for speech-to-text
- **Vector Database**: Qdrant for vector storage

## Prerequisites

- Docker and Docker Compose
- Python 3.8 or higher
- pip3
- virtualenv
- Available ports: 8000, 3000, 3001, 11434, 8080, 9090, 9000, 6333

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ThijsdeZeeuw/AVGKWINTES.git
cd AVGKWINTES
```

2. Make the setup script executable:
```bash
chmod +x setupkwintes.sh
```

3. Run the setup script:
```bash
./setupkwintes.sh
```

The script will:
- Check for prerequisites
- Set up a Python virtual environment
- Install required Python packages
- Create necessary data directories
- Generate secrets and configuration
- Start all services

## Available AI Models

The following AI models are available through Ollama:

1. gemma3:12b
   - Source: Google
   - Description: 12B parameter model with excellent performance

2. granite-embedding:278m
   - Source: IBM
   - Description: Efficient embedding model for text similarity

3. granite3-guardian:8b
   - Source: IBM
   - Description: 8B parameter model with security focus

4. llama2:13b
   - Source: Meta
   - Description: 13B parameter model with strong performance

5. llama2:7b
   - Source: Meta
   - Description: 7B parameter model with good performance

6. mistral:7b
   - Source: Mistral AI
   - Description: 7B parameter model with excellent performance and instruction-following capabilities

7. mistral-embedding:7b
   - Source: Mistral AI
   - Description: Embedding model for text similarity

## Service Access

After installation, you can access the services at:

- n8n: https://n8n.kwintes.cloud
- Flowise: https://flowise.kwintes.cloud
- WebUI: https://openwebui.kwintes.cloud
- Supabase: https://supabase.kwintes.cloud
- Ollama: https://ollama.kwintes.cloud
- SearXNG: https://searxng.kwintes.cloud
- Grafana: https://grafana.kwintes.cloud
- Prometheus: https://prometheus.kwintes.cloud
- Whisper: https://whisper.kwintes.cloud
- Qdrant: https://qdrant.kwintes.cloud

## Security Features

- HTTPS encryption for all services
- Secure secret management
- Isolated containers
- Regular security updates
- Firewall configuration
- Access control and authentication

## Maintenance

To update the services:

```bash
docker-compose pull
docker-compose up -d
```

To view logs:

```bash
docker-compose logs -f
```

To stop services:

```bash
docker-compose down
```

## Support

For issues and support, please create an issue in the GitHub repository.
