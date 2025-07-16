# Docker Setup for CSV2Notion Neo

This directory contains Docker-related files for running CSV2Notion Neo in a containerized environment.

## Files

- **Dockerfile**: Defines the Docker image with Python 3.11 and Poetry
- **docker-bake.hcl**: Docker Buildx configuration for building the image
- **install_from_docker.sh**: Script to build and run the Docker container

## Usage

### From Project Root (Recommended)
```bash
./scripts/docker-run.sh
```

### From Docker Directory
```bash
cd docker
./install_from_docker.sh
```

## Container Details

- **Base Image**: Python 3.11-slim
- **Package Manager**: Poetry
- **Memory Limit**: 512MB
- **CPU Limit**: 1.0 cores
- **Port**: 2222 (SSH)
- **Volume Mount**: Current directory mounted to `/app`

## Container Access

The container runs in detached mode with SSH access on port 2222. You can connect to it using:

```bash
ssh -p 2222 root@localhost
```

## Development

The container is set up for development with:
- All project dependencies installed
- Source code mounted as a volume
- Poetry configured for system-wide installation 