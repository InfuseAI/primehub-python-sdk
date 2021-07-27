import json
import os

from primehub import Helpful, Module, cmd
from tests import BaseTestCase

os.environ['PRIMEHUB_SDK_LOG_LEVEL'] = 'DEBUG'


class FakeCommand(Helpful, Module):

    @cmd(name='cmd-no-args', description='action_no_args')
    def action_no_args(self):
        return dict(name='action_no_args')

    @cmd(name='cmd-arg-str', description='action_1_args')
    def action_arg_str(self, arg1: str):
        return dict(name='action_arg_str', arg1=arg1)

    # TODO support different types (only str for now)
    @cmd(name='cmd-arg-str-int', description='action_str_int_args')
    def action_arg_str_int(self, arg1: str, arg2: int):
        return dict(name='action_arg_str_int', arg1=arg1, arg2=arg2)

    # TODO support optional arguments
    @cmd(name='cmd-args-opts', description='action_optional_args', optionals=['arg2'])
    def action_arg_str_int_optional(self, arg1: str, arg2: int = None):
        return dict(name='action_arg_str_int_optional', arg1=arg1, arg2=arg2)

    def help_description(self):
        return "help message for fake-command"


class TestCommandGroupToCommandLine(BaseTestCase):

    def setUp(self) -> None:
        super(TestCommandGroupToCommandLine, self).setUp()

        # clean commands, add the FakeCommand
        self.sdk.register_command('test_sdk_to_cli', FakeCommand)

    def test_command_groups(self):
        output = self.cli_stderr(['app.py', '-h'])

        # verify cli_tests command group in the output
        c = [x for x in output.split('\n') if 'test_sdk_to_cli' in x]
        self.assertTrue(c and len(c) == 1, 'We should find the command-group "test" in the output')

        description = self.fake().help_description()
        self.assertTrue(description in c[0], 'We should find the help messages in the output')

    def test_action_help(self):
        # output = self.cli_stderr(['app.py', 'test_sdk_to_cli', '-h'])
        # TODO it will fail, not implemented it
        # self.assertTrue('action_no_args' in output)
        pass

    def fake(self) -> FakeCommand:
        return FakeCommand(self.sdk)

    def test_action_no_args(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-no-args'])
        self.assertEqual(output.strip(), json.dumps(self.fake().action_no_args()))

    def test_action_1_arg(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-arg-str', 'primehub-cli-with-1-arg'])
        self.assertEqual(output.strip(), json.dumps(self.fake().action_arg_str('primehub-cli-with-1-arg')))
