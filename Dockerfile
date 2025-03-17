FROM python:3.11-slim

WORKDIR /app

COPY . ./

RUN apt-get update && apt-get install -y \
    bash \
    curl \
    git && \
    rm -rf /var/lib/apt/lists/*

RUN curl -ssl https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-root && \
    rm -rf /root/.cache/pypoetry

EXPOSE 22

USER root

RUN pytest -v -s
CMD ["tail","-f","/dev/null"]
