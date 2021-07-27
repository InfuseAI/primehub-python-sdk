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

        # mock the result of fetching group info
        group_info = {
            'id': 'group-id',
            'name': 'config-set:group',
            'displayName': 'group-display-name'
        }
        self.mock_request.return_value = {'data': {'me': {'effectiveGroups': [group_info]}}}
        args = ['app.py', 'config', 'set-group', 'config-set:group']
        self.cli_stdout(args)

        # Verify new configuration has been prefixed with 'config:set'
        self.assert_config_with_prefix('config-set', PrimeHubConfig())

        # Verify group information updated
        # {
        #   me {
        #     effectiveGroups {
        #       id
        #       name
        #       displayName
        #     }
        #   }
        # }
        self.assertEqual(group_info, self.load_json_file(PrimeHubConfig().get_default_path())['group'])
