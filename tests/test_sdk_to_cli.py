import json
import os

from primehub import Helpful, Module, cmd
from primehub.utils.optionals import toggle_flag
from primehub.utils.permission import ask_for_permission
from tests import BaseTestCase


class FakeCommand(Helpful, Module):

    @cmd(name='cmd-no-args', description='action_no_args')
    def action_no_args(self):
        return dict(name='action_no_args')

    @cmd(name='cmd-arg-str', description='action_1_args')
    def action_arg_str(self, arg1: str):
        return dict(name='action_arg_str', arg1=arg1)

    @cmd(name='cmd-arg-str-int', description='action_str_int_args')
    def action_arg_str_int(self, arg1: str, arg2: int):
        return dict(name='action_arg_str_int', arg1=arg1, arg2=arg2)

    # Note: we support optional arguments with **kwargs
    @cmd(name='cmd-args-opts', description='action_optional_args', optionals=[('arg2', str), ('page', int)])
    def action_optional_args(self, arg1: str, **kwargs):
        result = dict(name='action_arg_str_int_optional', arg1=arg1)
        if 'arg2' in kwargs:
            result['arg2'] = kwargs['arg2']
        if 'page' in kwargs:
            result['page'] = kwargs['page']
        return result

    @cmd(name='cmd-only-opts', description='action_only_optionals', optionals=[('file', str)])
    def action_only_optionals(self, **kwargs):
        return kwargs

    @ask_for_permission
    @cmd(name='cmd-remove-it', description='the action acts when user say-yes')
    def action_in_danger(self, file_to_remove, **kwargs):
        os.unlink(file_to_remove)
        return dict(result=True)

    @ask_for_permission
    @cmd(name='cmd-remove-it-no-arg-type-1', description='the action acts when user say-yes', optionals=[('file', str)])
    def action_in_danger_no_arg_type_1(self, **kwargs):
        os.unlink(kwargs.get('file'))
        return dict(result=True)

    @ask_for_permission
    @cmd(name='cmd-remove-it-no-arg-type-2', description='the action acts when user say-yes')
    def action_in_danger_no_arg_type_2(self, **kwargs):
        os.unlink("test_ask_for_permission_no_arg_type2.txt")
        return dict(result=True)

    @cmd(name='recursive-toggle-flag', description='the action has a toggle flag',
         optionals=[('recursive', toggle_flag)])
    def action_toggle_flag(self, **kwargs):
        return kwargs

    @cmd(name='return-required-no-retruns', description='return none for return required', return_required=True)
    def return_required_but_no_returns(self):
        # got exit 1
        return None

    @cmd(name='return-required-with-retruns', description='return values for return required', return_required=True)
    def return_required_with_returns(self):
        # got exit 0
        return "I don't care"

    def help_description(self):
        return "help message for fake-command"


class TestCommandGroupToCommandLine(BaseTestCase):

    def setUp(self) -> None:
        super(TestCommandGroupToCommandLine, self).setUp()

        # clean commands, add the FakeCommand
        self.sdk.register_command('test_sdk_to_cli', FakeCommand)

    def fake(self) -> FakeCommand:
        return FakeCommand(self.sdk)

    def test_command_groups(self):
        output = self.cli_stderr(['app.py', '-h'])

        # verify cli_tests command group in the output
        c = [x for x in output.split('\n') if 'test_sdk_to_cli' in x]
        self.assertTrue(c and len(c) == 1, 'We should find the command-group "test" in the output')

        description = self.fake().help_description()
        self.assertTrue(description in c[0], 'We should find the help messages in the output')

    def test_action_help(self):
        output = self.cli_stderr(['app.py', 'test_sdk_to_cli', '-h'])
        self.assertTrue('action_no_args' in output)

    def test_action_no_args(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-no-args'])
        self.assertEqual(json.dumps(self.fake().action_no_args()), output.strip())

    def test_action_1_arg(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-arg-str', 'primehub-cli-with-1-arg'])
        self.assertEqual(json.dumps(self.fake().action_arg_str('primehub-cli-with-1-arg')), output.strip())

    def test_action_with_non_str_type(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-arg-str-int', 'str', '5566'])
        self.assertEqual(json.dumps(self.fake().action_arg_str_int('str', 5566)), output.strip())

    def test_action_with_optional_args(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-args-opts', 'arg1'])
        self.assertEqual(json.dumps(self.fake().action_optional_args('arg1')), output.strip())

        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-args-opts', 'arg1', '--arg2', 'arg2'])
        self.assertEqual(json.dumps(self.fake().action_optional_args('arg1', arg2='arg2')), output.strip())

        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-args-opts', 'arg1', '--page', '9527'])
        self.assertEqual(json.dumps(self.fake().action_optional_args('arg1', page=9527)), output.strip())

    def test_action_with_only_optionals(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-only-opts', '--file', 'filename'])
        self.assertEqual(json.dumps(self.fake().action_only_optionals(file='filename')), output.strip())

    def test_ask_for_permission_1_arg(self):
        file = self.tempfile()

        # the file will not be removed, because we don't have the flag `--yes-i-really-mean-it`
        self.assertTrue(os.path.exists(file))
        self.cli_stderr(['app.py', 'test_sdk_to_cli', 'cmd-remove-it', file])
        self.assertTrue(os.path.exists(file))

        # the file will be removed by the flag `--yes-i-really-mean-it`
        self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-remove-it', file, '--yes-i-really-mean-it'])
        self.assertFalse(os.path.exists(file))

    def test_ask_for_permission_no_arg_type1(self):
        file = self.tempfile()

        # the file will not be removed, because we don't have the flag `--yes-i-really-mean-it`
        self.assertTrue(os.path.exists(file))
        self.cli_stderr(['app.py', 'test_sdk_to_cli', 'cmd-remove-it-no-arg-type-1', '--file', file])
        self.assertTrue(os.path.exists(file))

        # the file will be removed by the flag `--yes-i-really-mean-it`
        self.cli_stdout(
            ['app.py', 'test_sdk_to_cli', 'cmd-remove-it-no-arg-type-1', '--file', file, '--yes-i-really-mean-it'])
        self.assertFalse(os.path.exists(file))

    def test_ask_for_permission_no_arg_type2(self):
        file_path_to_delete = "test_ask_for_permission_no_arg_type2.txt"
        with open(file_path_to_delete, "w") as fh:
            fh.write("empty")

        # the file will not be removed, because we don't have the flag `--yes-i-really-mean-it`
        self.assertTrue(os.path.exists(file_path_to_delete))
        self.cli_stderr(['app.py', 'test_sdk_to_cli', 'cmd-remove-it-no-arg-type-2'])
        self.assertTrue(os.path.exists(file_path_to_delete))

        # the file will be removed by the flag `--yes-i-really-mean-it`
        self.cli_stdout(['app.py', 'test_sdk_to_cli', 'cmd-remove-it-no-arg-type-2', '--yes-i-really-mean-it'])
        self.assertFalse(os.path.exists(file_path_to_delete))

    def test_toggle_flag(self):
        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'recursive-toggle-flag', '--recursive'])
        self.assertEqual(dict(recursive=True), json.loads(output))

        output = self.cli_stdout(['app.py', 'test_sdk_to_cli', 'recursive-toggle-flag'])
        self.assertEqual(dict(recursive=False), json.loads(output))

    def test_return_required(self):

        def invoke_cli_and_get_exit_code(argv: list):
            try:
                import sys
                from primehub import cli
                sys.argv = argv
                cli.main(sdk=self.sdk)
            except SystemExit as e:
                if e.code == 1:
                    self.assertEqual('', self.sdk.stdout.getvalue().strip())
                    self.assertEqual('', self.sdk.stderr.getvalue().strip())
                if e.code == 0:
                    self.assertNotEqual('', self.sdk.stdout.getvalue().strip())
                return e.code

        exit_code = invoke_cli_and_get_exit_code(['app.py', 'test_sdk_to_cli', 'return-required-no-retruns'])
        self.assertEqual(1, exit_code)

        exit_code = invoke_cli_and_get_exit_code(['app.py', 'test_sdk_to_cli', 'return-required-with-retruns'])
        self.assertEqual(0, exit_code)
