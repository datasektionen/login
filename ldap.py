from ldap3 import Server, Connection, ALL



def get_user_info(ugid):
        server = Server("ldap.kth.se", port = 389, get_info=ALL)
        conn = Connection(server,  auto_bind=False)
        conn.bind()

        searchParameters = { 'search_base': 'ou=Addressbook,dc=kth,dc=se',
                             'search_filter': '(ugKthid=%s)' % ugid,
                             'attributes': ['givenname', 'sn', 'ugusername', 'mail', 'ugkthid'],
                             'paged_size': 1 }
        conn.search(**searchParameters)
        if conn.entries:
            entry = conn.entries[0]
            return {
                'first_name' : entry.givenName,
                'second_name': entry.sn,
                'user' : entry.ugUsername,
                'ugkthid' : entry.ugkthid
            }
        return None

if __name__ == "__main__":
    print(get_user_info("u1gch8hn"))
