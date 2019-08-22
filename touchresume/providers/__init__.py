from collections import UserDict

from flask import current_app, url_for
from werkzeug.local import LocalProxy

from .provider import ProviderError
from .headhunter import HeadHunter
from .superjob import SuperJob


__all__ = ['Providers', 'ProviderError']


class Providers(UserDict):

    def __init__(self, app=None):
        self.data = dict()

        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app, callback):
        user_agent = f'{app.name} v{app.version}'
        sj_redir_url = url_for(callback, provider='superjob', _external=True)

        app.extensions = getattr(app, 'extensions', {})
        app.extensions['touchresume'] = {}

        if app.config['HH_CLIENT_ID'] and app.config['HH_CLIENT_SECRET']:
            app.extensions['touchresume']['headhunter'] = HeadHunter(
                user_agent=user_agent,
                client_id=app.config['HH_CLIENT_ID'],
                client_secret=app.config['HH_CLIENT_SECRET'])

        if app.config['SJ_CLIENT_ID'] and app.config['SJ_CLIENT_SECRET']:
            app.extensions['touchresume']['superjob'] = SuperJob(
                user_agent=user_agent,
                client_id=app.config['SJ_CLIENT_ID'],
                client_secret=app.config['SJ_CLIENT_SECRET'],
                redirect_uri=sj_redir_url)

        self.data = LocalProxy(lambda: current_app.extensions['touchresume'])

        @app.context_processor
        def template_inject():
            return dict(providers=self)
