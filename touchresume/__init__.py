from os import path
from logging.config import dictConfig

from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from flask_migrate import Migrate
from flask_htmlmin import HTMLMIN
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery
from cerberus import Validator
from sentry_sdk import init as init_sentry
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .providers import Providers
from .schema import AppConfigSchema
from .config import AppConfig, LoggingConfig


__version__ = '1.1.0'


db = SQLAlchemy()
migrate = Migrate()
providers = Providers()
celery = Celery(__name__)
ma = Marshmallow()
cache = Cache()
login = LoginManager()
csrf = CSRFProtect()
cors = CORS()
htmlmin = HTMLMIN()
toolbar = DebugToolbarExtension()


def create_app(config=None):
    app = Flask(__name__)
    app.version = __version__

    dictConfig(LoggingConfig)

    app.config.from_object(AppConfig)
    if config:  # pragma: no cover
        app.config.from_object(config)

    validator = Validator(AppConfigSchema, allow_unknown=True)
    conf = validator.normalized(app.config, always_return_document=True)
    if not validator.validate(conf):  # pragma: no cover
        raise RuntimeError(f'Config validation failed {validator.errors}')

    app.config.update(conf)

    db.init_app(app)
    migrate.init_app(app, db, directory=path.join(app.root_path, 'migrations'))
    cors.init_app(app, origins=app.config['SERVER_NAME'])
    celery.conf.update(broker_url=app.config['REDIS_URL'])
    login.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    ma.init_app(app)
    htmlmin.init_app(app)
    toolbar.init_app(app)

    from .views import views
    app.register_blueprint(views)

    with app.app_context():  # url_for
        providers.init_app(app, 'views.login')

    dsn = app.config.get('SENTRY_DSN')
    if dsn and (not app.testing):  # pragma: no cover
        init_sentry(
            dsn=dsn, environment='development' if app.debug else 'production',
            integrations=[
                FlaskIntegration(), SqlalchemyIntegration(),
                RedisIntegration(), CeleryIntegration()])

    return app
