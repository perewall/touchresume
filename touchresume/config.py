from os import environ

from dotenv import load_dotenv


load_dotenv('.env')


class AppConfig(object):

    SERVER_NAME = environ.get('SERVER_NAME')
    SECRET_KEY = environ.get('SECRET_KEY')
    LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')

    REDIS_URL = environ.get('REDIS_URL')

    SENTRY_DSN = environ.get('SENTRY_DSN')

    HH_CLIENT_ID = environ.get('HH_CLIENT_ID')
    HH_CLIENT_SECRET = environ.get('HH_CLIENT_SECRET')

    SJ_CLIENT_ID = environ.get('SJ_CLIENT_ID')
    SJ_CLIENT_SECRET = environ.get('SJ_CLIENT_SECRET')

    TOUCH_INTERVAL = environ.get('TOUCH_INTERVAL')
    REAUTH_INTERVAL = environ.get('REAUTH_INTERVAL')
    CLEANUP_TASKS_INTERVAL = environ.get('CLEANUP_TASKS_INTERVAL')
    CLEANUP_RESUME_INTERVAL = environ.get('CLEANUP_RESUME_INTERVAL')
    CLEANUP_ACCOUNTS_INTERVAL = environ.get('CLEANUP_ACCOUNTS_INTERVAL')
    CLEANUP_USERS_INTERVAL = environ.get('CLEANUP_USERS_INTERVAL')


LoggingConfig = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'propagate': True
    },
    'formatters': {
        'app_format': {
            'style': '{',
            'format':
                '[{asctime}] [{process}] [{levelname}] '
                '[{module}.{funcName}] {message}'
        }
    },
    'handlers': {
        'app': {
            'class': 'logging.StreamHandler',
            'formatter': 'app_format'
        }
    },
    'loggers': {
        'touchresume': {
            'level': AppConfig.LOG_LEVEL,
            'handlers': ['app']
        }
    }
}
