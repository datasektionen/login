import psycopg2
import os
import random
import hashlib


# Does this location suck? :D Clean up this mess if you want to.
def gen_hash(salt):
    data = str(random.randint(0,100000000000)) + str(salt)
    return hashlib.md5(data.encode('utf-8')).hexdigest()

class Database:
    def __init__(self):
        self._connection = psycopg2.connect(os.getenv('DATABASE_URL'))

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()

    def update_time_created(self, token):
        cur = self._connection.cursor()
        query = '''
        UPDATE tokens
        SET time_created = NOW()
        WHERE token = %s
        '''
        num_updated = cur.execute(query, (token,))
        self.commit()
        cur.close()
        return num_updated

    def token_by_kthid(self, kthid):
        cur = self._connection.cursor()
        query = '''
        SELECT token
        FROM tokens
        WHERE kthid = %s
        AND time_created > NOW() - interval '1 day'
        LIMIT 1
        '''
        cur.execute(query, (kthid,))
        res = cur.fetchone()
        if res:
            res = res[0]
        else:
            res = None
        cur.close()
        self.commit()
        return res

    def kthid_by_token(self, token):
        cur = self._connection.cursor()
        query = '''
        SELECT kthid
        FROM tokens
        WHERE token = %s
        AND time_created > NOW() - interval '1 day'
        LIMIT 1
        '''
        cur.execute(query, (token,))
        res = cur.fetchone()

        cur.close()
        if not res:
            return None
        self.update_time_created(token)
        return res[0]


    def api_key_exists(self, api_key):

        cur = self._connection.cursor()
        query = '''
        SELECT 1
        FROM api_keys
        WHERE api_key = %s
        LIMIT 1
        '''
        cur.execute(query, (api_key,))
        res = cur.fetchone()
        self.commit()
        cur.close()

        return not not res


    def new_token(self, kthid):
        cur = self._connection.cursor()

        query = '''
        INSERT INTO tokens (token, kthid, time_created)
        VALUES (%s, %s, NOW())
        '''

        while cur.rowcount <= 0:
            new_token = gen_hash(kthid)
            cur.execute(query, (new_token, kthid))

        self.commit()
        cur.close()
        return new_token

    def new_api_key(self, prefix):
        cur = self._connection.cursor()

        query = '''
        INSERT INTO api_keys (api_key, time_created)
        VALUES (%s, NOW())
        '''
        while cur.rowcount <= 0:
            key_postfix = gen_hash(prefix)
            api_key = prefix + "-" + key_postfix
            cur.execute(query, (api_key,))
        self.commit()
        cur.close()
        return api_key

    # Shitty hack so i dont need to re-generate all api keys
    def insert_api_key(self, api_key):
        cur = self._connection.cursor()
        query = '''
        INSERT INTO api_keys (api_key, time_created)
        VALUES (%s, NOW())
        '''
        try:
            cur.execute(query, (api_key,))
        except:
            print
            pass
        self.commit()
        cur.close()
