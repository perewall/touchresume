from uuid import uuid4

from flask import url_for
from flask_wtf.csrf import generate_csrf
from responses import activate

from touchresume import providers
from touchresume.models import Account, Resume

from tests import TestApp
from tests.mock import FakeModels, FakeResponses, MockResponses


class TestView(TestApp):

    def assertResponseRedirect(self, response, pattern):
        self.assertEqual(response.status_code, 302)
        self.assertIn(pattern, response.location)

    def test_view_error(self):
        response = self.client.post(url_for('views.main'))
        self.assertEqual(response.status_code, 405)
        self.assertIn(url_for('views.main'), response.get_data(as_text=True))

    def test_view_main(self):
        FakeModels.task()
        for provider in providers.values():
            self.auth_user(FakeModels.user(), last_provider=provider.name)
            response = self.client.get(url_for('views.main'))
            self.assertEqual(response.status_code, 200)

    def test_view_logout(self):
        self.auth_user(FakeModels.user())
        response = self.client.get(url_for('views.logout'))

        self.assertResponseRedirect(response, url_for('views.main'))

    @activate
    def test_view_login(self):
        for provider in providers.values():
            MockResponses.provider_tokenize_access(provider)
            MockResponses.provider_identity(provider)

            url = url_for('views.login', provider=provider.name, code=123)
            response = self.client.get(url)

            self.assertResponseRedirect(response, url_for('views.resume'))

        self.assertEqual(Account.query.count(), len(providers))

    @activate
    def test_view_login_again(self):
        for provider in providers.values():
            identity = f'{uuid4()}'
            MockResponses.provider_tokenize_access(provider)
            MockResponses.provider_identity(provider, identity=identity)
            FakeModels.account(provider, identity)

            url = url_for('views.login', provider=provider.name, code=123)
            response = self.client.get(url)

            self.assertResponseRedirect(response, url_for('views.resume'))

        self.assertEqual(Account.query.count(), len(providers))

    def test_view_login_redirect(self):
        for provider in providers.values():
            url = url_for('views.login', provider=provider.name)
            response = self.client.get(url)

            self.assertResponseRedirect(response, provider.oauth.client_id)

    def test_view_login_unknown_provider(self):
        response = self.client.get(url_for('views.login', provider='xyz'))

        self.assertResponseRedirect(response, url_for('views.main'))

    @activate
    def test_view_login_provider_error(self):
        for provider in providers.values():
            MockResponses.provider_tokenize_access(provider)
            MockResponses.provider_identity(provider, code=400)

            url = url_for('views.login', provider=provider.name, code=123)
            response = self.client.get(url)

            self.assertFalse(Account.query.all())
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith(url_for('views.main')))

    def test_view_accounts(self):
        for provider in providers.values():
            user = FakeModels.user()
            FakeModels.account(provider=provider, user=user)

            self.auth_user(user=user)
            response = self.client.get(url_for('views.accounts'))

            self.assertEqual(response.status_code, 200)

    @activate
    def test_view_resume(self):
        for provider in providers.values():
            body = FakeResponses.resume(provider.name)
            MockResponses.provider_fetch(provider, body=body)

            user = FakeModels.user()
            account = FakeModels.account(provider=provider, user=user)

            self.auth_user(user=user)
            response = self.client.get(url_for('views.resume'))
            same_account = Account.query.get(account.identity)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(same_account.resume)

    @activate
    def test_view_resume_provider_error(self):
        for provider in providers.values():
            MockResponses.provider_fetch(provider, body=dict(), code=401)

            user = FakeModels.user()
            account = FakeModels.account(provider=provider, user=user)

            self.auth_user(user=user)
            response = self.client.get(url_for('views.resume'))
            same_account = Account.query.get(account.identity)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(same_account.resume)

    def test_view_resume_switch(self):
        for provider in providers.values():
            user = FakeModels.user()
            account = FakeModels.account(provider=provider, user=user)
            resume = FakeModels.resume(account=account, provider=provider)
            self.auth_user(user=user)

            body = dict(id=resume.identity)
            response = self.client.post(
                url_for('views.switch'), data=body,
                headers={'X-CSRFToken': generate_csrf()})
            same_resume = Resume.query.get(resume.identity)

            self.assertFalse(same_resume.autoupdate)
            self.assertEqual(response.status_code, 400)

            another_resume = FakeModels.resume(provider=provider)
            body = dict(resume=another_resume.identity)
            response = self.client.post(url_for('views.switch'), data=body)
            same_resume = Resume.query.get(another_resume.identity)

            self.assertFalse(same_resume.autoupdate)
            self.assertEqual(response.status_code, 404)

            body = dict(resume=resume.identity)
            response = self.client.post(url_for('views.switch'), data=body)
            same_resume = Resume.query.get(resume.identity)

            self.assertTrue(same_resume.autoupdate)
            self.assertEqual(response.status_code, 200)
