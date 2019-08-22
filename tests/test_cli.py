from touchresume import cli

from tests import TestApp


class CliTest(TestApp):

    def setUp(self):
        super().setUp()
        self.click = self.app.test_cli_runner()

    def test_cli_db_create(self):
        result = self.click.invoke(cli.db_create)

        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)

    def test_cli_db_purge(self):
        result = self.click.invoke(cli.db_purge)

        self.assertIsNotNone(result.exception)
        self.assertEqual(result.exit_code, 1)

        result = self.click.invoke(cli.db_purge, input='y')

        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
