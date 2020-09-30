# https://hub.docker.com/_/python
FROM python:3.7

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install

COPY *.py run.sh ./
COPY mockldap ./mockldap

# command in docker-compose.yml
# CMD ["./run.sh"]
