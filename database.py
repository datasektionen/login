import psycopg2
import os
import secrets
import hashlib

# Does this location suck? :D Clean up this mess if you want to.
def gen_hash(salt):
    data = secrets.token_bytes(20) + salt.encode("utf-8")
    return hashlib.sha3_256(data).hexdigest()

def gen_api_key(prefix):
    return prefix + "-" + gen_hash(prefix)

class Database:
    def __init__(self):
        self._connection = psycopg2.connect(os.getenv('DATABASE_URL'))
        self._connection.autocommit = True

    def __del__(self):
        self._connection.close()

    def update_time_created(self, token):
        with self._connection.cursor() as cur: 
            cur.execute('''
                UPDATE tokens
                SET time_created = NOW()
                WHERE token = %s
            ''', (token,))

    def token_by_kthid(self, kthid):
        with self._connection.cursor() as cur:
            cur.execute('''
                SELECT token
                FROM tokens
                WHERE kthid = %s
                AND time_created > NOW() - interval '1 day'
                LIMIT 1
            ''', (kthid,))
            res = cur.fetchone()
        if not res:
            return None
        return res[0]
        
    def kthid_by_token(self, token):
        with self._connection.cursor() as cur:
            cur.execute('''
                SELECT kthid
                FROM tokens
                WHERE token = %s
                AND time_created > NOW() - interval '1 day'
                LIMIT 1
            ''', (token,))
            res = cur.fetchone()
        if not res:
            return None
        return res[0]

    def api_key_exists(self, api_key):
        with self._connection.cursor() as cur:
            cur.execute('''
                SELECT 1
                FROM api_keys
                WHERE api_key = %s
                LIMIT 1
            ''', (api_key,))
            res = cur.fetchone()
        return not not res

    def new_token(self, kthid):
        query = '''
            INSERT INTO tokens (token, kthid, time_created)
            VALUES (%s, %s, NOW())
        '''
        with self._connection.cursor() as cur:
            # Query will fail if token is a duplicate since it is a primary key.
            # Retry until it works.
            while cur.rowcount <= 0:
                new_token = gen_hash(kthid)
                cur.execute(query, (new_token, kthid))
        return new_token

    def new_api_key(self, prefix):
        query = '''
            INSERT INTO api_keys (api_key, time_created)
            VALUES (%s, NOW())
        '''
        with self._connection.cursor() as cur:
            # Query will fail if api_key is a duplicate since it is a primary
            # key. Retry until it works.
            while cur.rowcount <= 0:
                api_key = gen_api_key(prefix)
                cur.execute(query, (api_key,))
        return api_key

    def delete_tokens(self, kthid):
        with self._connection.cursor() as cur:
            cur.execute('''
                DELETE FROM tokens
                WHERE kthid = %s
            ''', (kthid,))

    def delete_token(self, token):
        with self._connection.cursor() as cur:
            cur.execute('''
                DELETE FROM tokens
                WHERE token = %s
            ''', (token,))
