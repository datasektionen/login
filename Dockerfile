FROM python:3.6

WORKDIR /login3
COPY . /consignment_predictor/

RUN pip install -r requrements.txt

RUN python3 db_migrate

expose 5000
ENV FLASK_APP=server.py

CMD flask run --host 0.0.0.0