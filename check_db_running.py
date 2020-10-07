import psycopg2
import os
import time

while True:
    try:
        psycopg2.connect(os.getenv('DATABASE_URL'))
        print("Connected!", flush=True)
        break
    except Exception as e:
        # flush=True is added so that output is shown when running
        # docker-compose up.
        print(e, flush=True)
        print("Failed to connect to db... trying again in 1 s", flush=True)
        time.sleep(1)
