from datetime import datetime, timedelta

from requests.exceptions import HTTPError

from .provider import BaseProvider, ProviderError, TouchLimitError


class HeadHunter(BaseProvider):

    def __init__(self, **kwargs):
        super().__init__(  # nosec
            name='headhunter', base_url='https://api.hh.ru/',
            authorize_url='https://hh.ru/oauth/authorize',
            access_token_url='https://hh.ru/oauth/token', **kwargs)
        self.short_name = 'hh'
        self.identity_url = 'me'
        self.fetch_url = 'resumes/mine'
        self.touch_url = 'resumes/{0}/publish'
        self.touch_limit = timedelta(hours=4)
        self.touch_limit_error = (429, 'touch_limit_exceeded')

    def _parse_resume(self, item):
        pub_date = datetime.strptime(item['updated_at'], '%Y-%m-%dT%H:%M:%S%z')
        return dict(
            identity=f'{self.short_name}_{item["id"]}', title=item['title'],
            published=pub_date.isoformat(), link=item['alternate_url'],
            photo=item['photo']['small'] if item['photo'] else None)

    @property
    def redirect_url(self):
        return self.oauth.get_authorize_url(
            response_type='code', skip_choose_account='true')

    def tokenize(self, code, refresh=False):
        if not refresh:
            body = {'code': f'{code}', 'grant_type': 'authorization_code'}
        else:
            body = {'refresh_token': f'{code}', 'grant_type': 'refresh_token'}

        try:
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
            return [self._parse_resume(item) for item in rv.json()['items']]

    def touch(self, token, resume):
        try:
            url = self.touch_url.format(resume.strip(f'{self.short_name}_'))
            rv = self.oauth.get_session(token=token).post(
                url, headers=self.headers)
            rv.raise_for_status()
        except HTTPError as e:
            if self._is_touch_limit_error(e):
                raise TouchLimitError(provider=self, error=e)
            raise ProviderError(provider=self, error=e)
        else:
            return True
