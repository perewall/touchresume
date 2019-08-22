AppConfigSchema = {
    'SERVER_NAME': {
        'type': 'string',
        'required': True
    },
    'SECRET_KEY': {
        'type': 'string',
        'required': True
    },
    'CACHE_TYPE': {
        'type': 'string',
        'required': True,
        'default': 'simple'
    },
    'MINIFY_PAGE': {
        'type': 'boolean',
        'required': True,
        'default': True
    },
    'SQLALCHEMY_DATABASE_URI': {
        'type': 'string',
        'required': True
    },
    'REDIS_URL': {
        'type': 'string',
        'required': True
    },
    'HH_CLIENT_ID': {
        'type': 'string',
        'required': True,
        'nullable': True,
        'default': None
    },
    'HH_CLIENT_SECRET': {
        'type': 'string',
        'required': True,
        'nullable': True,
        'default': None
    },
    'SJ_CLIENT_ID': {
        'type': 'string',
        'required': True,
        'nullable': True,
        'default': None
    },
    'SJ_CLIENT_SECRET': {
        'type': 'string',
        'required': True,
        'nullable': True,
        'default': None
    },
    'SENTRY_DSN': {
        'type': 'string',
        'required': True,
        'nullable': True,
        'default': None
    },
    'TASKS_LIMIT': {
        'type': 'integer',
        'required': True,
        'coerce': int,
        'min': 0,
        'default': 5,
    },
    'TOUCH_INTERVAL': {
        'type': 'integer',
        'required': True,
        'coerce': int,
        'min': 60,
        'default': 60*30  # 30 min
    },
    'REAUTH_INTERVAL': {
        'type': 'integer',
        'required': True,
        'coerce': int,
        'min': 60,
        'default': 60*60  # 1 hour
    },
    'CLEANUP_TASKS_INTERVAL': {
        'type': 'integer',
        'required': True,
        'coerce': int,
        'min': 60,
        'default': 60*40  # 40 min
    },
    'CLEANUP_RESUME_INTERVAL': {
        'type': 'integer',
        'required': True,
        'coerce': int,
        'min': 60,
        'default': 60*60*3  # 3 hours
    },
    'CLEANUP_ACCOUNTS_INTERVAL': {
        'type': 'integer',
        'required': True,
        'coerce': int,
        'min': 60,
        'default': 60*60*24  # 24 hours
    },
    'CLEANUP_USERS_INTERVAL': {
        'type': 'integer',
        'required': True,
        'coerce': int,
        'min': 60,
        'default': 60*60*24*3  # 3 days
    }
}
