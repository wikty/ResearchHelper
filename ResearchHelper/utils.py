import re
import string
import random

def id_generator(n=6, chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(chars) for _ in range(n))


# Improve the Flask-SQLAlchemy automatcially generate table name mechanism.
camelcase_re = re.compile(r'([A-Z]+)(?=([a-z0-9]|$))')

def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1 and match.end() < len(name):
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return camelcase_re.sub(_join, name).lstrip('_')