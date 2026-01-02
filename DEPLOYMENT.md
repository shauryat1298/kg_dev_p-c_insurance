# Docker Deployment Guide

This guide explains how to deploy the Insurance Data Model Builder application using Docker.

## Prerequisites

- Docker Engine 20.10 or later
- Docker Compose 2.0 or later
- A `.env` file with required API keys (see Configuration section)

## Quick Start

1. **Create a `.env` file** in the project root with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   # Add other API keys as needed (OpenRouter, etc.)
   ```

2. **Build and start the container**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

4. **View logs**:
   ```bash
   docker-compose logs -f streamlit-app
   ```

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root directory with the following variables:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Override base path (defaults to project root)
BASE_PATH=/app

# Add other environment variables as needed by your application
```

**Note**: The `.env` file is excluded from version control (see `.gitignore`). Make sure to create it before running the container.

### Volume Mounts

The `docker-compose.yml` file mounts the `artifacts/` directory as a volume to ensure data persistence:

- **PDF files** uploaded through the UI
- **PNG images** generated from PDFs
- **Proto data models** created during processing
- **ChromaDB database** with embeddings and entities

All data in the `artifacts/` directory will persist across container restarts and rebuilds.

## Building the Image

### Using Docker Compose (Recommended)

```bash
# Build the image
docker-compose build

# Build without cache (for clean rebuild)
docker-compose build --no-cache
```

### Using Docker Directly

```bash
# Build the image
docker build -t lob-kg-dev:latest .

# Run the container
docker run -d \
  --name lob-kg-dev-app \
  -p 8501:8501 \
  -v $(pwd)/artifacts:/app/artifacts \
  --env-file .env \
  lob-kg-dev:latest
```

## Managing the Container

### Start the service
```bash
docker-compose up -d
```

### Stop the service
```bash
docker-compose down
```

### Restart the service
```bash
docker-compose restart
```

### View logs
```bash
# Follow logs in real-time
docker-compose logs -f streamlit-app

# View last 100 lines
docker-compose logs --tail=100 streamlit-app
```

### Execute commands in the container
```bash
docker-compose exec streamlit-app bash
```

### Check container status
```bash
docker-compose ps
```

## Troubleshooting

### Port Already in Use

If port 8501 is already in use, modify the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8502:8501"  # Change 8501 to your preferred port
```

Then access the app at `http://localhost:8502`

### Permission Issues with Artifacts Directory

If you encounter permission issues with the artifacts directory:

```bash
# On Linux/Mac
sudo chown -R $USER:$USER artifacts/

# Or adjust permissions
chmod -R 755 artifacts/
```

### Container Won't Start

1. Check logs for errors:
   ```bash
   docker-compose logs streamlit-app
   ```

2. Verify `.env` file exists and contains required variables:
   ```bash
   cat .env
   ```

3. Ensure Docker has enough resources allocated (memory, CPU)

### Missing Dependencies

If you encounter import errors, rebuild the image:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### ChromaDB Issues

If ChromaDB data appears corrupted or missing:

1. Stop the container
2. Check the `artifacts/chroma_db_client/` directory
3. If needed, remove the ChromaDB data and restart (this will reset the database):
   ```bash
   rm -rf artifacts/chroma_db_client/*
   docker-compose restart
   ```

## Production Deployment

For production deployment, consider:

1. **Use a reverse proxy** (nginx, Traefik) in front of the Streamlit app
2. **Enable HTTPS** with SSL certificates
3. **Set resource limits** in `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
       reservations:
         cpus: '1'
         memory: 2G
   ```
4. **Use Docker secrets** or a secrets management service for API keys
5. **Set up logging** to an external service
6. **Configure backups** for the `artifacts/` volume
7. **Use a managed database** instead of local ChromaDB for scalability

## Updating the Application

To update the application after code changes:

```bash
# Rebuild the image
docker-compose build

# Restart the service
docker-compose up -d
```

Or in one command:

```bash
docker-compose up -d --build
```

## Health Checks

The container includes a health check that verifies the Streamlit app is responding. Check health status:

```bash
docker-compose ps
```

The status column will show "healthy" when the app is running correctly.

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit Documentation](https://docs.streamlit.io/)

