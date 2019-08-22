from unittest import TestCase

from responses import activate, reset

from touchresume.providers import HeadHunter, SuperJob, ProviderError

from tests.mock import FakeResponses, MockResponses


class TestProvider(object):

    def test_provider_redirect(self):
        result = self.provider.redirect_url

        self.assertIn(self.provider.oauth.authorize_url, result)
        self.assertIn(self.provider.oauth.client_id, result)

    @activate
    def test_provider_tokenize_access(self):
        MockResponses.provider_tokenize_access(self.provider)

        result = self.provider.tokenize('qwerty')

        self.assertIn('access_token', result)
        self.assertIn('refresh_token', result)

    @activate
    def test_provider_tokenize_refresh(self):
        MockResponses.provider_tokenize_refresh()

        result = self.provider.tokenize('qwerty', refresh=True)

        self.assertIn('access_token', result)
        self.assertIn('refresh_token', result)

    @activate
    def test_provider_tokenize_error(self):
        MockResponses.provider_tokenize_access(self.provider, code=400)

        with self.assertRaises(ProviderError) as e:
            self.provider.tokenize('qwerty')

        self.assertEqual(e.exception.code, 400)

    @activate
    def test_provider_identity(self):
        MockResponses.provider_identity(self.provider, identity='12345')

        result = self.provider.identity('qwerty')

        self.assertIn('12345', result)

    @activate
    def test_provider_identity_error(self):
        MockResponses.provider_identity(self.provider, code=401)

        with self.assertRaises(ProviderError) as e:
            self.provider.identity('qwerty')

        self.assertEqual(e.exception.code, 401)

    @activate
    def test_provider_fetch(self):
        body = FakeResponses.resume(self.provider.name)
        MockResponses.provider_fetch(self.provider, body=body)

        result = self.provider.fetch('qwerty')

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    @activate
    def test_provider_fetch_error(self):
        body = FakeResponses.resume(self.provider.name)
        MockResponses.provider_fetch(self.provider, body=body, code=500)

        with self.assertRaises(ProviderError) as e:
            self.provider.fetch('qwerty')

        self.assertEqual(e.exception.code, 500)

    @activate
    def test_provider_touch(self):
        MockResponses.provider_touch(self.provider, identity='123')

        result = self.provider.touch('qwerty', '123')

        self.assertTrue(result)

    @activate
    def test_provider_touch_error(self):
        MockResponses.provider_touch(self.provider, identity='123', code=503)

        with self.assertRaises(ProviderError) as e:
            self.provider.touch('qwerty', '123')

        self.assertEqual(e.exception.code, 503)


class HeadHunterTest(TestCase, TestProvider):

    def setUp(self):
        reset()
        self.provider = HeadHunter(client_id='fake', client_secret='test')


class SuperJobTest(TestCase, TestProvider):

    def setUp(self):
        reset()
        self.provider = SuperJob(
            client_id='fake', client_secret='test', redirect_uri='url')
