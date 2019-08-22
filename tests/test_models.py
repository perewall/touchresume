from touchresume.models import db, Account, Resume

from tests import TestApp
from tests.mock import FakeModels


class ModelsTest(TestApp):

    def test_model_cascade_delete(self):
        user = FakeModels.user()

        account = FakeModels.account(user=user)
        self.assertIn(account, user.accounts)
        self.assertTrue(Account.query.all())

        resume = FakeModels.resume(account=account)
        self.assertIn(resume, account.resume)
        self.assertTrue(Resume.query.all())

        db.session.delete(user)
        db.session.commit()

        self.assertFalse(Account.query.all())
        self.assertFalse(Resume.query.all())
