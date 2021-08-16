import inspect

from primehub.utils.decorators import __requires_permission__
from tests import BaseTestCase


class TestAskForPermissionMethods(BaseTestCase):

    def test_verify_ask_for_permissions(self):
        commands = __requires_permission__.keys()
        for cmd in commands:
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
