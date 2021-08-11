import json

from primehub import Helpful, Module, cmd, PrimeHubConfig
from tests import BaseTestCase


class ConfigWatcher(Helpful, Module):

    @cmd(name='watch', description='watch-primehub-config')
    def watch(self):
        # ensure the config file is changed
        assert self.primehub.primehub_config.config_file != self.primehub.primehub_config.get_default_path()

        from tempfile import mkstemp
        fd, path = mkstemp('.json', text=True)
        self.primehub.primehub_config.save(path=path)

        return dict(config_file=path)

    def help_description(self):
        return "Big Brother Watch YOU"


class TestCliConfig(BaseTestCase):

    def setUp(self) -> None:
        super(TestCliConfig, self).setUp()

        # clean commands, add the FakeCommand
        self.sdk.register_command('test_cli_config', ConfigWatcher)

    def test_config_options(self):
        """
        Global Options:
          --config CONFIG      the path of the config file
          --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
          --token TOKEN        API Token generated from PrimeHub Console
          --group GROUP        override the active group
        """
        group_info = {'name': 'test-config-from-cli:group'}
        self.mock_request.return_value = {'data': {'me': {'effectiveGroups': [group_info]}}}
        c = self.make_cfg()

        # Verify the saved config will have test-config-from-cli:*
        self.assert_config_with_prefix('test-config-from-cli', c)

        # Verify other options
        group_info = {'name': 'opt:group'}
        self.mock_request.return_value = {'data': {'me': {'effectiveGroups': [group_info]}}}
        c = self.make_cfg(['--endpoint', 'opt:endpoint', '--token', 'opt:api-token', '--group', 'opt:group'])
        self.assert_config_with_prefix('opt', c)

    def make_cfg(self, extra_args: list = None):
        if extra_args is None:
            extra_args = []

        cfg_path = self.create_fake_config(self.cfg_dict_with_prefix('test-config-from-cli'))
        output = self.cli_stdout(['app.py', 'test_cli_config', 'watch', '--config', cfg_path] + extra_args)

        # bug: the output buffer contains the previous result, we only take the last one
        output = output.strip().split("\n")[-1]

        saved_cfg_path = json.loads(output)['config_file']
        new_cfg = PrimeHubConfig(config=saved_cfg_path)
        return new_cfg
