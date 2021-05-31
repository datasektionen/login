import os
from ldap3 import Server, Connection, ALL, MOCK_SYNC

def get_connection():
        if os.environ.get('MOCK_LDAP', '0') == '1':
                # https://ldap3.readthedocs.io/en/latest/mocking.html
                server = Server("fake_server")
                conn = Connection(server, client_strategy=MOCK_SYNC)
                conn.strategy.entries_from_json("mockldap/mock_ldap_entries.json")
                return conn
        else:
                server = Server('ldap.kth.se', port=389, get_info=ALL)
                return Connection(server, auto_bind=False)

def get_user_info(email):
        conn = get_connection()
        conn.bind()
        search_params = { 'search_base': 'ou=Addressbook,dc=kth,dc=se',
                          'search_filter': '(mail=%s)' % email,
                          'attributes': ['givenname', 'sn', 'ugusername', 'mail', 'ugkthid'],
                          'paged_size': 1 }
        conn.search(**search_params)
        if conn.entries:
                entry = conn.entries[0]
                return {
                        'first_name' : entry.givenName.values[0],
                        'last_name': entry.sn.values[0],
                        'user' : entry.ugUsername.values[0],
                        'emails': entry.mail.values[0],
                        'ugkthid' : entry.ugkthid.values[0]
                }
        return None

if __name__ == "__main__":
    print(get_user_info("u1gch8hn"))
