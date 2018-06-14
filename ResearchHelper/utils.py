import os
import re
import uuid
import hashlib
import string
import random

def rlid_generator(n=6, chars=string.ascii_letters+string.digits):
    """Generate a random fixed length string."""
    return ''.join(random.choice(chars) for _ in range(n))


def uuid_generator():
    """Generate a UUID string.
    Note: A UUID contains 32 hexadecimal digits, its format is `8-4-4-12`.
    """
    return str(uuid.uuid4())


# Improve the Flask-SQLAlchemy automatcially generate table name mechanism.
camelcase_re = re.compile(r'([A-Z]+)(?=([a-z0-9]|$))')

def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1 and match.end() < len(name):
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return camelcase_re.sub(_join, name).lstrip('_')


def file_fingerprint(file):
    """Get file content md5 check sum.
    :param file: a byte string is file content. a string is file path.
     Or a file object(with read() method).
    """
    hash_md5 = hashlib.md5()
    if isinstance(file, bytes):
        hash_md5.update(bytes) 
    elif isinstance(file, str):
        with open(file, "rb") as f:
            # read by chunk so it's able to load a big file
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    elif callable(getattr(file, 'read', None)):
        # read by chunk so it's able to load a big file
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    else:
        return None
    return hash_md5.hexdigest()


def file_uniquename(dirname=None, ext=''):
    """Get a unique file name of a directory."""
    uid = rlid_generator(32)
    filename = '.'.join([uid, ext]).rstrip('.')
    if (not dirname) or (not os.path.isdir(dirname)):
        return filename
    while True:
        if not os.path.isfile(os.path.join(dirname, filename)):
            return filename
        uid = rlid_generator(32)
        filename = '.'.join([uid, ext]).rstrip('.')


def split_delimiter_quoted_str(s, delimiter=',', quote='"'):
    # https://stackoverflow.com/questions/16710076/python-split-a-string-respect-and-preserve-quotes
    return re.findall(
        r'(?:[^\s{d}{q}]|{q}(?:\\.|[^{q}])*{q})+'.format(d=delimiter, q=quote), 
        s
    )
