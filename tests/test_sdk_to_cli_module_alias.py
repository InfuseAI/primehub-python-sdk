import json

from primehub import Helpful, Module, cmd
from tests import BaseTestCase


class FakeCommandBehindAlias(Helpful, Module):

    @cmd(name='cmd-no-args', description='action_no_args')
    def action_no_args(self):
        return dict(name='action_no_args')

    def help_description(self):
        return "help message for fake-command"


class TestCommandGroupAlias(BaseTestCase):

    def setUp(self) -> None:
        super(TestCommandGroupAlias, self).setUp()

        # clean commands, add the FakeCommand
        self.sdk.register_command('module_name_with_dash_alias', FakeCommandBehindAlias, 'module-name-with-dash-alias')

    def fake(self) -> FakeCommandBehindAlias:
        return FakeCommandBehindAlias(self.sdk)

    def test_command_groups_with_cli(self):
        output = self.cli_stdout(['app.py', 'module-name-with-dash-alias', 'cmd-no-args'])
        self.assertEqual(dict(name='action_no_args'), json.loads(output))

    def test_command_groups_with_sdk(self):
        output = self.sdk.module_name_with_dash_alias.action_no_args()
        self.assertEqual(dict(name='action_no_args'), output)
