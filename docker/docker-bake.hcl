group "default" {
    targets = ["neo_python"]
}

target "neo_python" {
  context = ".."
  dockerfile = "docker/Dockerfile"
  tags = ["neo_python:latest"]
}
