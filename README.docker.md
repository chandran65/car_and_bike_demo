# Docker Setup for Mahindra Bot Streamlit App

This guide explains how to run the Mahindra Bot Streamlit app using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)
- OpenAI API key

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Set up environment variables:**
   ```bash
   # Create a .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

2. **Build and run the container:**
   ```bash
   docker-compose up --build
   ```

3. **Access the app:**
   Open your browser and navigate to `http://localhost:8501`

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. **Build the Docker image:**
   ```bash
   docker build -t mahindra-bot-app .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -p 8501:8501 \
     -e OPENAI_API_KEY=your_api_key_here \
     --name mahindra-bot \
     mahindra-bot-app
   ```

3. **Access the app:**
   Open your browser and navigate to `http://localhost:8501`

4. **Stop and remove the container:**
   ```bash
   docker stop mahindra-bot
   docker rm mahindra-bot
   ```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `STREAMLIT_SERVER_PORT`: Port for Streamlit (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)

### Custom Port

To run on a different port (e.g., 8080):

**Docker Compose:**
```yaml
ports:
  - "8080:8501"
```

**Docker:**
```bash
docker run -d -p 8080:8501 -e OPENAI_API_KEY=your_api_key_here mahindra-bot-app
```

## Troubleshooting

### Container won't start

Check logs:
```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs mahindra-bot
```

### Playwright issues

The Dockerfile installs Chromium and its dependencies. If you encounter issues:

1. Ensure you have enough disk space (Chromium needs ~200MB)
2. Check logs for specific error messages

### API Key not working

Make sure:
1. The `.env` file exists and contains the correct API key
2. For Docker directly, the environment variable is properly set with `-e`

## Development

### Rebuilding after code changes

```bash
# Docker Compose
docker-compose up --build

# Docker
docker build -t mahindra-bot-app .
docker run -d -p 8501:8501 -e OPENAI_API_KEY=your_api_key_here mahindra-bot-app
```

### Mounting local code for development

Add this to `docker-compose.yml` volumes:
```yaml
volumes:
  - ./src:/app/src
  - ./streamlit_apps:/app/streamlit_apps
```

## Production Deployment

For production deployments, consider:

1. **Use multi-stage builds** to reduce image size
2. **Set resource limits** in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
   ```

3. **Enable HTTPS** using a reverse proxy (nginx, traefik)
4. **Use secrets management** instead of .env files
5. **Add monitoring and logging**

## Image Size

The Docker image is approximately 1.5-2GB due to:
- Python runtime
- Playwright Chromium browser
- Python dependencies

To reduce size, you can:
- Use a multi-stage build
- Remove playwright if not needed
- Use pip instead of uv (slightly smaller)
