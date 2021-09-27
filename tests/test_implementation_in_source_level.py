import inspect
import os

from primehub.utils.decorators import __requires_permission__
from tests import BaseTestCase


class TestAskForPermissionMethods(BaseTestCase):

    def test_verify_ask_for_permissions(self):
        commands = __requires_permission__.keys()
        for cmd in commands:
            if "test" in cmd:
                continue
            # cmd will look like 'primehub.schedules.delete'
            package_name, command_name, method_name = cmd.split(".")

            if package_name != 'primehub':
                # only cares about primehub package
                continue

            cmd_obj = self.sdk.commands[command_name]
            method = getattr(cmd_obj, method_name)

            # check the "**kwargs" in the last parameter
            signature = inspect.signature(method)
            signature = [str(x) for x in signature.parameters.values()]

            if not signature:
                self.report_bad_method_signature(cmd, method)

            if signature[-1] != '**kwargs':
                self.report_bad_method_signature(cmd, method)

    def report_bad_method_signature(self, cmd, method):
        src, lines = inspect.getsourcelines(method)
        delimeter = '.' * 80
        report = f'\n{delimeter} \nCommand: {cmd} \nLine: {lines}\n{"".join(src[:5])}\n{delimeter}'
        raise ValueError(
            f'@ask_for_permission must have a "**kwargs" in the last parameter, please update: {cmd}{report}')


class TestDocumentation(BaseTestCase):
    """
    There should be 3 document files for a command.

    A notebook:
    ./docs/notebook/{command}.ipynb

    A generated command line doc:
    ./docs/CLI/{command}.md

    An example will embedded into cli doc:
    ./primehub/extras/templates/examples/{command}.ipynb
    """

    def test_verify_ask_for_permissions(self):
        project_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

        def generate_doc_paths(command):
            files = [
                f'./docs/notebook/{command}.ipynb',
                f'./docs/CLI/{command}.md',
                f'./primehub/extras/templates/examples/{command}.md'
            ]
            return [os.path.normpath(os.path.join(project_dir, x)) for x in files]

        for command in self.sdk.commands:

            # skip version command
            if command == 'version':
                continue

            notebook, cli, cli_example = generate_doc_paths(command)

            if not os.path.exists(notebook):
                raise ValueError(f'There should have a {notebook} for command "{command}"')

            if not os.path.exists(cli):
                raise ValueError(f'There should have a {cli} for command "{command}"')

            if not os.path.exists(cli_example):
                raise ValueError(f'There should have a {cli_example} for command "{command}"')
