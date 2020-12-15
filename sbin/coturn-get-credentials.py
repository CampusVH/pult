import hashlib
import hmac
import base64
from time import time
from sys import argv

user = argv[1]
secret = argv[2]

ttl = 24 * 3600 # Time to live
timestamp = int(time()) + ttl
username = str(timestamp) + ':' + user
dig = hmac.new(secret, username, hashlib.sha1).digest()
password = base64.b64encode(dig).decode()

print('%s %s' % (username, password))
