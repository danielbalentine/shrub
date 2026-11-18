FROM docker.io/library/python:3.12-slim
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt
WORKDIR /shrub