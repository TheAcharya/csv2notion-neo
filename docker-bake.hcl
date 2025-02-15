group "default" {
    targets = ["neo_python"]
}

target "neo_python" {
  context = "."
  dockerfile = "Dockerfile"
  tags = ["neo_python:latest"]
