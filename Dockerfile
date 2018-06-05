FROM python:3.6

WORKDIR /login3
COPY . /login3/


RUN pip install -r requirements.txt

expose 5000
ENV FLASK_APP=/login3/server.py
RUN cd /login3
RUN cat server.py
CMD flask run --host 0.0.0.0