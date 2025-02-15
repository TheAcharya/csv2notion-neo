FROM python:3.12-slim

WORKDIR /app

COPY . ./

RUN apt-get update && apt-get install -y \
    bash \
    curl \
    openssh-server \
    git && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash neouser && \
    echo "neouser:password" | chpasswd && \
    usermod -u 0 -o neouser

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN curl -ssl https://install.python-poetry.org | python3 - && \
mv /root/.local/bin/poetry /usr/local/bin/poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-root && \
    rm -rf /root/.cache/pypoetry

EXPOSE 22

USER root

RUN mkdir -p /run/sshd && chmod 0755 /run/sshd

#CMD ["tail","-f","/dev/null"]
CMD ["/usr/sbin/sshd","-D"]