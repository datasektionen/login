from ldap3 import Server, Connection, ALL



def get_user_info(ugid):
        server = Server("ldap.kth.se", port=389, get_info=ALL)
        conn = Connection(server, auto_bind=False)
        conn.bind()
        search_params = { 'search_base': 'ou=Addressbook,dc=kth,dc=se',
                          'search_filter': '(ugKthid=%s)' % ugid,
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
