#!/bin/bash
pipenv run python check_db_running.py
pipenv run python db_migrate.py
pipenv run python genkey.py testing
pipenv run gunicorn wsgi:app -b 0.0.0.0:8000 --log-file -
