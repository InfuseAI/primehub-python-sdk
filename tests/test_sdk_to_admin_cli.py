import json

from primehub import Helpful, Module, cmd
from tests import BaseTestCase


class FakeCommand(Helpful, Module):

    @cmd(name='list', description='action_no_args')
    def action_no_args(self):
        return [1, 2, 3]

    def help_description(self):
        return "helpful"


class TestAdminCommandGroupToCommandLine(BaseTestCase):

    def setUp(self) -> None:
        super(TestAdminCommandGroupToCommandLine, self).setUp()

        # clean commands, add the FakeCommand
        self.sdk.register_admin_command('test_datasets', FakeCommand)

    def fake(self) -> FakeCommand:
        return FakeCommand(self.sdk)

    def test_primehub_admin(self):
        output = self.cli_stdout(['app.py', 'admin', 'test_datasets', 'list'])
        self.assertEqual([1, 2, 3], json.loads(output))

    def test_primehub_admin_help(self):
        output = self.cli_stderr(['app.py', 'admin', 'test_datasets', '-h'])
        usage = [x.strip() for x in output.split('\n') if '<command>' in x][0]
        self.assertEqual('primehub admin test_datasets <command>', usage)
