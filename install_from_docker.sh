IMAGE_NAME="neo_python:latest"
CONTAINER_NAME="neo_python_container"

# Building the image
docker buildx bake

# Creating a container from that image and running it 
<<<<<<< HEAD
docker run --name $CONTAINER_NAME -d --memory="512m" --cpus="1.0" -v $(pwd):/app -p 2222:22 $IMAGE_NAME
=======
docker run --name $CONTAINER_NAME -d --memory="512m" --cpus="1.0" -p 2222:22 $IMAGE_NAME
>>>>>>> aa99d5122a0c6520102c809fbaca9be9fab4a13f
