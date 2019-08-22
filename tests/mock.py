import re
from uuid import uuid4
from urllib.parse import urljoin
from datetime import datetime, timedelta

from responses import add

from touchresume.models import db, User, Account, Resume, Task


class FakeProvider(object):

    name = 'fake'
    short_name = 'fk'


class Fake(object):

    @staticmethod
    def make_identity(prefix, identity=None):
        if not identity:
            return f'{prefix}_{uuid4()}'
        elif not identity.startswith(prefix):
            return f'{prefix}_{identity}'
        return identity


class FakeResponses(Fake):

    @classmethod
    def token(cls, expires=60):
        return {
            'access_token': cls.make_identity('access'),
            'refresh_token': cls.make_identity('refresh'),
            'expires_in': expires
        }

    @classmethod
    def resume(cls, provider):
        data = {
            'headhunter': {
                'items': [{
                    'id': cls.make_identity('resume'),
                    'updated_at': '2019-07-16T00:38:10+0300',
                    'photo': None,
                    'title': 'manager',
                    'alternate_url': 'http://example.com'
                }]
            },
            'superjob': {
                'objects': [{
                    'id': cls.make_identity('resume'),
                    'date_published': 1563226690,
                    'photo': None,
                    'profession': 'manager',
                    'link': 'http://example.com'
                }]
            }
        }
        return data[provider]


class FakeModels(Fake):

    @staticmethod
    def commit(obj):
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def user(cls, identity=None):
        identity = cls.make_identity('usr', identity)
        user = User(identity=identity)
        return cls.commit(user)

    @classmethod
    def account(cls, provider=FakeProvider, identity=None, user=None):
        identity = cls.make_identity(provider.short_name, identity)
        if not user:
            user = cls.user()
        account = Account(
            identity=identity, access='access', refresh='refresh',
            expires=datetime.utcnow() + timedelta(seconds=10),
            provider=provider.name, user=user)
        return cls.commit(account)

    @classmethod
    def resume(
            cls, account=None, provider=FakeProvider,
            identity=None, autoupdate=False, old=False):
        if not account:
            account = cls.account(provider=provider)
        identity = cls.make_identity(provider.short_name, identity)
        resume = Resume(
            identity=identity, autoupdate=autoupdate, account=account)
        if old:
            resume.published = (datetime.utcnow() - (provider.touch_limit * 2))
        return cls.commit(resume)

    @classmethod
    def task(cls, identity=None, name='fake'):
        identity = cls.make_identity('tsk', identity)
        now = datetime.utcnow()
        task = Task(
            identity=identity, started_at=now, finished_at=now,
            success=0, skipped=0, total=0, name=name)
        return cls.commit(task)


class MockResponses(object):

    @staticmethod
    def provider_tokenize_access(provider, body=None, code=200):
        url = provider.oauth.access_token_url
        body = body or FakeResponses.token()
        add(method='POST', url=url, json=body, status=code)

    @staticmethod
    def provider_tokenize_refresh(body=None, code=200):
        url = re.compile(r'.*')
        body = body or FakeResponses.token()
        add(method='GET', url=url, json=body, status=code)
        add(method='POST', url=url, json=body, status=code)

    @staticmethod
    def provider_identity(provider, identity=None, code=200):
        if not identity:
            identity = uuid4()
        body = dict(id=f'{identity}')
        url = urljoin(provider.oauth.base_url, provider.identity_url)
        add(method='GET', url=url, json=body, status=code)

    @staticmethod
    def provider_fetch(provider, body, code=200):
        url = urljoin(provider.oauth.base_url, provider.fetch_url)
        add(method='GET', url=url, json=body, status=code)

    @staticmethod
    def provider_touch(provider, identity, code=200):
        identity = identity.strip(f'{provider.short_name}_')
        push_url = provider.touch_url.format(identity)
        url = urljoin(provider.oauth.base_url, push_url)
        add(method='POST', url=url, status=code)
