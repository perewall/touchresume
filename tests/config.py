from os import environ

from touchresume.config import AppConfig


class TestConfig(AppConfig):

    TESTING = True

    SERVER_NAME = 'local'
    SECRET_KEY = 'test'

    WTF_CSRF_ENABLED = False

    CACHE_TYPE = 'null'

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL', 'sqlite://')

    REDIS_URL = environ.get('TEST_REDIS_URL', 'redis://')

    HH_CLIENT_ID = 'fake'
    HH_CLIENT_SECRET = 'test'

    SJ_CLIENT_ID = 'fake'
    SJ_CLIENT_SECRET = 'test'

    TASKS_LIMIT = 2
