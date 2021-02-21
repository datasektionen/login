# https://hub.docker.com/_/python
FROM python:3.8

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install

COPY mockldap ./mockldap
COPY *.py run.sh CHECKS ./

CMD ["./run.sh"]
