# https://hub.docker.com/_/python
FROM python:3

WORKDIR /usr/src/app

COPY server.py .
COPY data_dir ./data_dir

# command in docker-compose.yml
# CMD ["python3", "server.py", "--port", "8001", "rudolf", "data_dir"]
