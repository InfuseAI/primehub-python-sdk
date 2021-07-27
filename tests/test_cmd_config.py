from primehub import PrimeHubConfig
from tests import BaseTestCase


class TestCmdConfig(BaseTestCase):

    def setUp(self) -> None:
        super(TestCmdConfig, self).setUp()

    def test_config_options(self):
        """
        Usage:
          primehub config [command]

        Update the settings of PrimeHub SDK

        Available Commands:
          set-endpoint         set endpoint and save to the config file
          set-token            set token and save to the config file
          set-group            set group and save to the config file
        """

        # use cli version's config
        self.sdk.register_command('config', 'CliConfig')

        args = ['app.py', 'config', 'set-endpoint', 'config-set:endpoint']
        self.cli_stdout(args)

        args = ['app.py', 'config', 'set-token', 'config-set:api-token']
        self.cli_stdout(args)

        args = ['app.py', 'config', 'set-group', 'config-set:group']
        self.cli_stdout(args)

        self.assert_config_with_prefix('config-set', PrimeHubConfig())
