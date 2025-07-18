# Docker Deployment Guide

This guide covers how to run the Dar.ai PDF Service using Docker for both development and production environments.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- `.env` file with required environment variables

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

## Development Deployment

### Using Docker Compose (Recommended)

1. **Build and run the service:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f comparison-api
   ```

4. **Stop the service:**
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t comparison-api .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name comparison-api \
     -p 8000:8000 \
     --env-file .env \
     -v $(pwd)/data:/app/data:ro \
     comparison-api
   ```

## Production Deployment

### Using Production Docker Compose

1. **Build and run with production configuration:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. **Monitor the service:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f comparison-api
   ```

### Using Production Dockerfile

1. **Build the production image:**
   ```bash
   docker build -f Dockerfile.prod -t comparison-api:prod .
   ```

2. **Run the production container:**
   ```bash
   docker run -d \
     --name comparison-api-prod \
     -p 8000:8000 \
     --env-file .env \
     --restart unless-stopped \
     comparison-api:prod
   ```

## Service Health Check

The service includes built-in health checks accessible at:
- Basic health: `http://localhost:8000/`
- Detailed health: `http://localhost:8000/health`

You can check the health status with:
```bash
curl http://localhost:8000/health
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

- `GET /compare` - Generate property comparison PDF
- `GET /quote` - Generate property quote PDF
- `GET /recommend` - Generate personalized recommendation PDF
- `GET /properties` - List available properties
- `GET /contacts` - List available contacts

## Container Management

### View running containers:
```bash
docker ps
```

### View container logs:
```bash
docker logs comparison-api
```

### Execute commands in running container:
```bash
docker exec -it comparison-api bash
```

### Stop and remove containers:
```bash
docker stop comparison-api
docker rm comparison-api
```

### Remove images:
```bash
docker rmi comparison-api
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change the port mapping in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Environment variables not loading:**
   - Ensure `.env` file exists in the project root
   - Check that `OPENROUTER_API_KEY` is set correctly

3. **Data files not found:**
   - Ensure `data/properties.json` and `data/contacts.json` exist
   - Check file permissions

4. **Health check failing:**
   ```bash
   # Check if the service is responding
   curl -f http://localhost:8000/health
   ```

### Debug Mode

To run the container in debug mode:
```bash
docker run -it --rm \
  --env-file .env \
  -p 8000:8000 \
  comparison-api \
  bash
```

## Production Considerations

- The production Dockerfile uses multi-stage builds for smaller image size
- Resource limits are configured in `docker-compose.prod.yml`
- Logging is configured with rotation to prevent disk space issues
- Health checks are configured for automatic container restart
- The service runs as a non-root user for security

## Security Notes

- Never commit `.env` files with real API keys
- Use Docker secrets for sensitive data in production
- Regularly update base images for security patches
- Consider using a reverse proxy (nginx) in production 