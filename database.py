import psycopg2
import os
import random
import hashlib

print(os.environ)

class Database:
    def __init__(self):
        self._connection = psycopg2.connect(os.environ['DATABASE_URL'])


    def token_by_kthid(self, kthid):
        cur = self._connection.cursor()
        query = '''
        SELECT token
        FROM tokens
        WHERE kthid = %s
        LIMIT 1
        '''
        cur.execute(query, kthid)
        res = cur.fetchone()
        if res:
            res = res['token']
        else:
            res = None
        cur.close()
        return res

    def kthid_by_token(self, token):
        cur  = self._connection.cursor()
        query = '''
        SELECT uid
        FROM tokens
        WHERE token = %s AND to_timestamp(time_created) < NOW() - INTERVAL '30 days'
        LIMIT 1
        '''
        res = cur.execute(query, token)
        cur.close()
        if not res:
            return None
        else:
            return res["kthid"]


    def api_key_exists(self, api_key):

        cur = self._connection.cursor()
        query = '''
        SELECT 1
        FROM api_keys
        WHERE api_key = %s
        LIMIT 1
        '''
        cur.execute(query, api_key)
        res = cur.fetchone()
        cur.close()
        return not not res



    def new_token(self, kthid):
        cur = self._connection.cursor()

        query = '''
        INSERT INTO tokens (token, kthid, time_created)
        VALUES (%s, %s, NOW())
        '''
        while cur.rowcount > 0:
            new_token = hashlib.md5(str(random.random(0,100000000000)) + kthid).hexdigest()
            cur.execute(query, new_token, kthid)

        cur.close()
        return new_token

    def new_api_key(self, prefix):
        cur = self._connection.cursor()

        query = '''
        INSERT INTO api_keys (api_key, time_created)
        VALUES (%s, NOW())
        '''
        while cur.rowcount > 0:
            key_postfix = hashlib.md5(str(random.random(0,100000000000)) + prefix).hexdigest()
            api_key = prefix + key_postfix
            cur.execute(query, api_key)
        cur.close()
        return api_key

    # Shitty hack so i dont need to re-generate all api keys
    def insert_api_key(self, api_key):
        cur = self._connection.cursor()
        query = '''
        INSERT INTO api_keys (api_key, time_created)
        VALUES (%s, NOW())
        '''
        cur.execute(query, api_key)
        cur.close()
