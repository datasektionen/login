import psycopg2
import os

print(os.getenv('DATABASE_URL'))

connection = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = connection.cursor()




## List of queries to create database, list append shit
migrations =  [
    '''
    CREATE TABLE api_keys (
    api_key varchar(255) PRIMARY KEY,
    time_created date NOT NULL
    );
    ''',
    '''
    CREATE TABLE tokens (
    token varchar(255) PRIMARY KEY,
    kthid varchar(255) NOT NULL,
    time_created date NOT NULL
    )
    '''
]



for n, query in enumerate(migrations):
    print("#### MIGRATION %s of %s ####" % (n, len(migrations)))
    print(query)
    cur.execute(query)

cur.close()

print("##### MIGRATION DONE #####")
