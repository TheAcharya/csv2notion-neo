#!/bin/bash

IMAGE_NAME="neo_python:latest"
CONTAINER_NAME="neo_python_container"

# Change to project root directory
cd ..

# Building the image
docker buildx bake -f docker/docker-bake.hcl

# Creating a container from that image and running it 
docker run --name $CONTAINER_NAME -d --memory="512m" --cpus="1.0" -v $(pwd):/app -p 2222:22 $IMAGE_NAME
