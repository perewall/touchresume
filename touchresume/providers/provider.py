from urllib.parse import urlparse

from rauth import OAuth2Service


class ProviderError(Exception):

    def __init__(self, provider, error, *args, **kwargs):
        self.provider = provider
        self.code = error.response.status_code
        self.request = error.request
        self.response = error.response
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.code}, reason={self.response.text}'


class TouchLimitError(ProviderError):
    """Raises when resume is already updated"""


class BaseProvider(object):

    def __init__(self, user_agent=None, **kwargs):
        self.oauth = OAuth2Service(**kwargs)
        self.headers = {'User-Agent': user_agent or self.oauth.name}

    @property
    def name(self):
        return self.oauth.name

    @property
    def website(self):
        url = urlparse(self.oauth.authorize_url)
        return f'{url.scheme}://{url.netloc}'

    def _is_touch_limit_error(self, e):
        code = self.touch_limit_error[0]
        msg = self.touch_limit_error[1]
        try:
            text = e.response.json()
        except Exception:
            text = e.response.text
        return (e.response.status_code == code) and (msg in str(text).lower())
