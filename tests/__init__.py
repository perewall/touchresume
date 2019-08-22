from unittest import TestCase, main

from responses import reset

from touchresume import db, create_app

from .config import TestConfig


class TestApp(TestCase):

    def setUp(self, config=TestConfig):
        self.app = create_app(config)
        self.client = self.app.test_client()

        self.app_context = self.app.test_request_context()
        self.app_context.push()

        self.db = db
        self.db.init_app(self.app)
        self.db.create_all()

    def tearDown(self):
        self.db.session.rollback()
        self.db.drop_all()
        self.app_context.pop()
        reset()

    def auth_user(self, user, last_provider=None):
        with self.client.session_transaction() as session:
            session['user_id'] = user.identity
            session['_fresh'] = True
            if last_provider:
                session['last_provider'] = last_provider


if __name__ == '__main__':
    main()
