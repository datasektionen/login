#!/bin/python3
import sys
from database import Database

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Provide a name for the key")
        exit()
    if len(sys.argv) > 2:
        print("Looks like you meant to add some quotes around that brah")
        exit()
    key_name = sys.argv[1]

    db = Database()
    new_key = db.new_api_key(key_name)
    print("Here's your new key %s \n Store it somewhere safe or look it up in the database when you forget it" % new_key)
