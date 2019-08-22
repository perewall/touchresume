from datetime import datetime, timedelta, timezone

from requests.exceptions import HTTPError

from .provider import BaseProvider, ProviderError


class SuperJob(BaseProvider):

    def __init__(self, redirect_uri, **kwargs):
        base_url = 'https://api.superjob.ru/2.0/'
        super().__init__(  # nosec
            name='superjob', base_url=base_url,
            authorize_url='https://www.superjob.ru/authorize/',
            access_token_url=f'{base_url}oauth2/access_token/', **kwargs)
        self.oauth.redirect_uri = redirect_uri
        self.short_name = 'sj'
        self.identity_url = 'user/current/'
        self.fetch_url = 'user_cvs/'
        self.touch_url = 'user_cvs/update_datepub/{0}/'
        self.touch_limit = timedelta(hours=1)
        self.headers.update({'X-Api-App-Id': self.oauth.client_secret})

    def _parse_resume(self, item):
        tz = timezone(timedelta(hours=3))
        pub_date = datetime.fromtimestamp(item['date_published'], tz=tz)
        return dict(
            identity=f'{self.short_name}_{item["id"]}',
            published=pub_date.isoformat(), title=item['profession'],
            link=item['link'], photo=item['photo'])

    @property
    def redirect_url(self):
        return self.oauth.get_authorize_url(
            redirect_uri=self.oauth.redirect_uri)

    def tokenize(self, code, refresh=False):
        body = dict(
            client_id=self.oauth.client_id,
            client_secret=self.oauth.client_secret)
        try:
            if refresh:
                body['refresh_token'] = code
                rv = self.oauth.get_session().get(  # custom refresh_token url
                   'https://api.superjob.ru/2.0/oauth2/refresh_token/',
                   headers=self.headers, params=body)
            else:
                body['code'] = code,
                body['redirect_uri'] = self.oauth.redirect_uri
                rv = self.oauth.get_raw_access_token(
                    data=body, headers=self.headers)
            rv.raise_for_status()
        except HTTPError as e:
            raise ProviderError(provider=self, error=e)
        else:
            return rv.json()

    def identity(self, token):
        try:
            rv = self.oauth.get_session(token=token).get(
                self.identity_url, headers=self.headers)
            rv.raise_for_status()
        except HTTPError as e:
            raise ProviderError(provider=self, error=e)
        else:
            return f'{self.short_name}_{rv.json()["id"]}'

    def fetch(self, token):
        try:
            rv = self.oauth.get_session(token=token).get(
                self.fetch_url, headers=self.headers)
            rv.raise_for_status()
        except HTTPError as e:
            raise ProviderError(provider=self, error=e)
        else:
            return [self._parse_resume(item) for item in rv.json()['objects']]

    def touch(self, token, resume):
        try:
            url = self.touch_url.format(resume.strip(f'{self.short_name}_'))
            rv = self.oauth.get_session(token=token).post(
                url, headers=self.headers)
            rv.raise_for_status()
        except HTTPError as e:
            raise ProviderError(provider=self, error=e)
        else:
            return True
