import string
import random

def id_generator(n=6, chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(chars) for _ in range(n))