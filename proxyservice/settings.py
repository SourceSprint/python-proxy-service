import os
import random
import gevent.monkey
from dotenv import load_dotenv

gevent.monkey.patch_all()
load_dotenv()


def generate_secret_key():
    random_string = ''

    for _ in range(20):
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        random_string += (chr(random_integer))

    return random_string


PYTHON_ENV = os.getenv('PYTHON_ENV')
IS_DEVELOPMENT = PYTHON_ENV == 'development'

SECRET_KEY = os.getenv('SECRET_KEY') or generate_secret_key()
FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT') or 9000
