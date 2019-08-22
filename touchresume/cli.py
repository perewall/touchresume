from flask import current_app
from flask.cli import FlaskGroup, with_appcontext
from flask_migrate.cli import db as migrate
from click import group, option, confirm
from gunicorn.app.base import BaseApplication
from redbeat import RedBeatScheduler
from sentry_sdk import init as init_sentry
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from . import create_app, db


def init_sentry_integration(app, integration):
    dsn = app.config.get('SENTRY_DSN')
    if dsn:
        env = 'development' if app.debug else 'production'
        init_sentry(dsn=dsn, environment=env, integrations=[integration()])


class GunicornApp(BaseApplication):

    def __init__(self, factory, **kwargs):
        self.options = kwargs
        self.app_factory = factory
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings:
                self.cfg.set(key.lower(), value)

    def load(self):
        app = self.app_factory()
        init_sentry_integration(app, FlaskIntegration)
        return app


@migrate.command('create')
@with_appcontext
def db_create():
    """Create all tables"""
    db.create_all()


@migrate.command('purge')
@with_appcontext
def db_purge():
    """Purge database schema"""
    if confirm('Do you really want to drop the database?', abort=True):
        db.drop_all()


@group(cls=FlaskGroup, create_app=create_app, set_debug_flag=False)
def cli():
    """TouchResume CLI"""


@cli.command()
@option('-w', '--workers', type=int, default=None, help='Number of workers')
@option('-l', '--loglevel', default='info', help='Celery logging level')
def tasks(workers, loglevel):
    """Run a tasks with Celery worker."""
    from .tasks import celery
    init_sentry_integration(current_app, CeleryIntegration)
    celery.Worker(
        beat=True, loglevel=loglevel.upper(),
        scheduler=RedBeatScheduler, concurrency=workers).start()


@cli.command(with_appcontext=False)
@option('-h', '--host', default='127.0.0.1', help='Binding address')
@option('-p', '--port', type=int, default=8000, help='Listening port')
@option('-w', '--workers', type=int, default=1, help='Number of workers')
@option('-l', '--loglevel', default='info', help='Gunicorn logging level')
@option('-t', '--timeout', type=int, default=30, help='Worker timeout')
def serve(host, port, workers, loglevel, timeout):
    """Run a production-ready server with Gunicorn."""
    GunicornApp(
        factory=create_app, worker_class='eventlet', bind=f'{host}:{port}',
        workers=workers, loglevel=loglevel, timeout=timeout).run()
