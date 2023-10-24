
from hashlib import md5
def md5_from_string(s):
    return md5(s.encode('utf-8')).hexdigest()

