# Docker Deployment Guide

This guide explains how to run the WebApp Firewall Simulator using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

### Install Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Other systems:** Visit https://docs.docker.com/get-docker/

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Navigate to project directory:**
   ```bash
   cd /home/zor0ark/Documents/WebAppFirewallSimulator
   ```

2. **Build and run:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Open browser: http://localhost:5000

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t webapp-firewall-simulator .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 --name firewall-sim webapp-firewall-simulator
   ```

3. **Access the application:**
   - Open browser: http://localhost:5000

4. **View logs:**
   ```bash
   docker logs -f firewall-sim
   ```

5. **Stop the container:**
   ```bash
   docker stop firewall-sim
   docker rm firewall-sim
   ```

## Docker Commands Reference

### Build Commands
```bash
# Build image
docker build -t webapp-firewall-simulator .

# Build with no cache
docker build --no-cache -t webapp-firewall-simulator .

# Build with custom tag
docker build -t webapp-firewall-simulator:v1.0 .
```

### Run Commands
```bash
# Run in foreground
docker run -p 5000:5000 webapp-firewall-simulator

# Run in background (detached)
docker run -d -p 5000:5000 --name firewall-sim webapp-firewall-simulator

# Run with custom port
docker run -d -p 8080:5000 --name firewall-sim webapp-firewall-simulator

# Run with auto-restart
docker run -d -p 5000:5000 --restart unless-stopped --name firewall-sim webapp-firewall-simulator
```

### Management Commands
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View logs
docker logs firewall-sim

# Follow logs (real-time)
docker logs -f firewall-sim

# Stop container
docker stop firewall-sim

# Start container
docker start firewall-sim

# Restart container
docker restart firewall-sim

# Remove container
docker rm firewall-sim

# Remove image
docker rmi webapp-firewall-simulator
```

### Docker Compose Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose up --build

# Stop and remove everything
docker-compose down -v
```

## Port Configuration

By default, the application runs on port 5000. You can change this:

**Docker CLI:**
```bash
docker run -d -p 8080:5000 --name firewall-sim webapp-firewall-simulator
```
Access at: http://localhost:8080

**Docker Compose:**
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"
```

## Environment Variables

You can customize the application using environment variables:

```bash
docker run -d -p 5000:5000 \
  -e FLASK_ENV=development \
  -e FLASK_DEBUG=1 \
  --name firewall-sim webapp-firewall-simulator
```

Or in `docker-compose.yml`:
```yaml
environment:
  - FLASK_ENV=development
  - FLASK_DEBUG=1
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs firewall-sim

# Check if port is already in use
sudo netstat -tulpn | grep 5000

# Try different port
docker run -d -p 8080:5000 --name firewall-sim webapp-firewall-simulator
```

### Can't access application
```bash
# Verify container is running
docker ps

# Check container status
docker inspect firewall-sim

# Test from inside container
docker exec -it firewall-sim curl http://localhost:5000
```

### Out of disk space
```bash
# Clean up unused images
docker image prune -a

# Clean up everything
docker system prune -a
```

### Permission denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then test
docker ps
```

## Production Deployment

### Using Docker Compose with nginx

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  firewall-simulator:
    build: .
    container_name: webapp-firewall-simulator
    expose:
      - "5000"
    environment:
      - FLASK_ENV=production
    restart: always

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - firewall-simulator
    restart: always
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Health Checks

The Docker Compose configuration includes health checks:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Check health status:
```bash
docker inspect firewall-sim | grep -A 10 Health
```

## Updating the Application

1. **Pull latest changes:**
   ```bash
   git pull
   ```

2. **Rebuild and restart:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

Or with Docker CLI:
```bash
docker stop firewall-sim
docker rm firewall-sim
docker build -t webapp-firewall-simulator .
docker run -d -p 5000:5000 --name firewall-sim webapp-firewall-simulator
```

## Backup and Restore

### Export container
```bash
docker export firewall-sim > firewall-sim-backup.tar
```

### Save image
```bash
docker save webapp-firewall-simulator > firewall-sim-image.tar
```

### Load image
```bash
docker load < firewall-sim-image.tar
```

## Multi-Platform Builds

Build for different architectures:
```bash
# Build for AMD64 and ARM64
docker buildx build --platform linux/amd64,linux/arm64 -t webapp-firewall-simulator .
```

## Resource Limits

Limit container resources:
```bash
docker run -d -p 5000:5000 \
  --memory="512m" \
  --cpus="1.0" \
  --name firewall-sim webapp-firewall-simulator
```

Or in `docker-compose.yml`:
```yaml
services:
  firewall-simulator:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

## Security Best Practices

1. **Run as non-root user** (add to Dockerfile):
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

2. **Use specific image versions:**
   ```dockerfile
   FROM python:3.12.0-slim
   ```

3. **Scan for vulnerabilities:**
   ```bash
   docker scan webapp-firewall-simulator
   ```

4. **Keep images updated:**
   ```bash
   docker pull python:3.12-slim
   docker build --no-cache -t webapp-firewall-simulator .
   ```

## Monitoring

### View resource usage
```bash
docker stats firewall-sim
```

### Inspect container
```bash
docker inspect firewall-sim
```

### Execute commands inside container
```bash
docker exec -it firewall-sim bash
```

## Support

For issues related to Docker deployment:
1. Check logs: `docker logs firewall-sim`
2. Verify Dockerfile and requirements.txt
3. Ensure ports are not in use
4. Check Docker daemon is running: `systemctl status docker`

---

**WebApp Firewall Simulator**  
Created by Van Glenndon Enad

For more information, see the main [README.md](README.md)
