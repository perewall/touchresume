from responses import activate

from touchresume import providers, tasks
from touchresume.models import User, Account, Resume, Task

from tests import TestApp
from tests.mock import FakeModels, MockResponses


class TasksTest(TestApp):

    def assertTaskResult(self, result, total, success, skipped=0):
        self.assertEqual(result['total'], total)
        self.assertEqual(result['success'], success)
        self.assertEqual(result['skipped'], skipped)

    @activate
    def test_task_touch_resume(self):
        for provider in providers.values():
            FakeModels.resume(provider=provider, autoupdate=True)
            resume = FakeModels.resume(
                provider=provider, autoupdate=True, old=True)
            MockResponses.provider_touch(provider, identity=resume.identity)

        result = tasks.touch_resume()

        prov = len(providers)
        self.assertTaskResult(result, total=prov*2, success=prov, skipped=prov)

    @activate
    def test_task_touch_resume_disable(self):
        for provider in providers.values():
            resume = FakeModels.resume(
                provider=provider, autoupdate=True, old=True)
            MockResponses.provider_touch(
                provider, identity=resume.identity, code=500)

            result = tasks.touch_resume()
            same_resume = Resume.query.get(resume.identity)

            self.assertFalse(same_resume.autoupdate)
            self.assertTaskResult(result, total=1, success=0, skipped=1)

    @activate
    def test_task_refresh_tokens(self):
        for provider in providers.values():
            MockResponses.provider_tokenize_refresh()
            FakeModels.account(provider=provider)

        result = tasks.refresh_tokens()

        total = len(providers)
        self.assertTaskResult(result, total=total, success=total)

    def test_task_cleanup_tasks(self):
        for _ in range(4):
            FakeModels.task()

        before_cleanup = Task.query.count()
        self.assertEqual(4, before_cleanup)

        result = tasks.cleanup_tasks(2)
        self.assertEqual(2, result)

        after_cleanup = Task.query.count()
        self.assertEqual(2, after_cleanup)

    def test_task_cleanup_users(self):
        user1, user2 = FakeModels.user(), FakeModels.user()
        FakeModels.account(user=user1)

        before_cleanup = User.query.all()
        self.assertIn(user1, before_cleanup)
        self.assertIn(user2, before_cleanup)

        result = tasks.cleanup_users()
        self.assertEqual(1, result)

        after_cleanup = User.query.all()
        self.assertIn(user1, after_cleanup)
        self.assertNotIn(user2, after_cleanup)

    def test_task_cleanup_accounts(self):
        account1 = FakeModels.account()
        account2 = FakeModels.account()
        FakeModels.resume(account=account1)

        before_cleanup = Account.query.all()
        self.assertIn(account1, before_cleanup)
        self.assertIn(account2, before_cleanup)

        result = tasks.cleanup_accounts()
        self.assertEqual(1, result)

        after_cleanup = Account.query.all()
        self.assertIn(account1, after_cleanup)
        self.assertNotIn(account2, after_cleanup)

    def test_task_cleanup_resume(self):
        resume1 = FakeModels.resume(autoupdate=True)
        resume2 = FakeModels.resume(autoupdate=False)

        before_cleanup = Resume.query.all()
        self.assertIn(resume1, before_cleanup)
        self.assertIn(resume2, before_cleanup)

        result = tasks.cleanup_resume()
        self.assertEqual(1, result)

        after_cleanup = Resume.query.all()
        self.assertIn(resume1, after_cleanup)
        self.assertNotIn(resume2, after_cleanup)
