# Docker Setup Guide

This guide explains how to run the LLM PDF Extractor application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- OpenAI API key

## Quick Start

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd llm-pdf-extractor
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env file and add your OpenAI API key
   ```

3. **Build and run the application:**
   ```bash
   # Build the Docker image
   make docker-build
   
   # Run the application
   make docker-run
   ```

4. **Access the application:**
   - Open your browser and navigate to `http://localhost:8501`
   - The Streamlit interface will be available

## Docker Commands

### Build the Image
```bash
docker build -t pdf-extractor .
```

### Run with Docker Compose
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Run Individual Container
```bash
# Run the container
docker run -d \
  --name pdf-extractor \
  -p 8501:8501 \
  -e OPENAI_API_KEY=your-api-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  pdf-extractor

# View logs
docker logs -f pdf-extractor

# Stop the container
docker stop pdf-extractor
docker rm pdf-extractor
```

## Docker Configuration

### Dockerfile Features
- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for monitoring
- **Optimized layer caching** for faster builds

### Docker Compose Features
- **Volume mounting** for persistent data storage
- **Environment variable** configuration
- **Health checks** and restart policies
- **Optional Redis** for caching (commented out)

### Volumes
- `./data:/app/data` - Database and application data
- `./uploads:/app/uploads` - Temporary file uploads

### Environment Variables
- `OPENAI_API_KEY` - Your OpenAI API key
- `STREAMLIT_SERVER_PORT` - Port for Streamlit (default: 8501)
- `STREAMLIT_SERVER_ADDRESS` - Bind address (default: 0.0.0.0)

## Production Deployment

### Using Docker Compose
```bash
# Production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.swarm.yml pdf-extractor
```

### Using Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

## Monitoring and Health Checks

### Health Check Endpoint
The application includes a health check endpoint at `/health` that Docker can use to monitor the application status.

### Logs
```bash
# View application logs
docker-compose logs -f pdf-extractor

# View specific log levels
docker-compose logs -f --tail=100 pdf-extractor
```

### Metrics
The application exposes basic metrics that can be monitored:
- Processing time per document
- Success/failure rates
- API response times

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using port 8501
   lsof -i :8501
   
   # Change port in docker-compose.yml
   ports:
     - "8502:8501"
   ```

2. **Permission denied errors:**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER data/ uploads/
   ```

3. **OpenAI API errors:**
   - Verify your API key is correct
   - Check API rate limits
   - Ensure sufficient credits

4. **Memory issues:**
   ```bash
   # Increase memory limits
   docker run --memory=2g pdf-extractor
   ```

### Debug Mode
```bash
# Run with debug logging
docker run -e LOG_LEVEL=DEBUG pdf-extractor

# Access container shell
docker exec -it pdf-extractor /bin/bash
```

## Performance Optimization

### Resource Limits
```yaml
# docker-compose.yml
services:
  pdf-extractor:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
```

### Scaling
```bash
# Scale horizontally
docker-compose up -d --scale pdf-extractor=3

# Load balancer configuration needed for multiple instances
```

## Security Considerations

- **Non-root user** in container
- **Read-only filesystem** where possible
- **Resource limits** to prevent abuse
- **Network isolation** with custom networks
- **Secrets management** for sensitive data

## Backup and Recovery

### Database Backup
```bash
# Backup database
docker exec pdf-extractor sqlite3 /app/data/pdf_extractor.db ".backup /app/data/backup.db"

# Copy backup from container
docker cp pdf-extractor:/app/data/backup.db ./backup.db
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v pdf-extractor_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build and Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t pdf-extractor .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push your-registry/pdf-extractor:latest
```

## Support

For issues related to Docker setup:
1. Check the troubleshooting section above
2. Review Docker and Docker Compose logs
3. Verify environment variable configuration
4. Check system resource availability
