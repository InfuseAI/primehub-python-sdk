import json
import os
import tempfile
from datetime import datetime
from shutil import copyfile
from urllib.parse import urlparse

import requests

from primehub import Helpful, cmd, Module
from primehub.utils import create_logger, group_not_found

logger = create_logger('cmd-config')


class Config(Helpful, Module):
    """
    The config module provides functions to update PrimeHubConfig.

    Config class only changes data in the memory,
    otherwise CliConfig will change data and update it to the real configuration file.

    In SDK mode, config will use Config.
    In Command mode, config will use CliConfig.
    CliConfig will update the file config after a `set_*` method call.
    """

    def set_endpoint(self, endpoint: str):
        """
        Set endpoint to the GraphQL API.

        It usually is in this pattern https://<primehub-domain>/api/graphql

        :type endpoint: str
        :param endpoint: an URL to GraphQL API endpoint
        """
        self.primehub.primehub_config.endpoint = endpoint

    def set_token(self, token: str):
        """
        Set api-token to the PrimeHubConfig

        :type token: str
        :param token: a token used by GraphQL request
        """
        self.primehub.primehub_config.api_token = token

    def set_group(self, group: str):
        """
        Set current group to work with group aware actions.

        When setting a group, it will validate the group. It the group is invalid, PrimeHub.current_group will be None.

        :type group: str
        :param group: group name
        """
        self.reconfigure_group(group, raise_error=True)

    def reconfigure_group(self, group, raise_error=False):
        if group is None:
            return
        selected_group = self._fetch_group_info(group)
        if selected_group is None:
            if raise_error:
                logger.warning(
                    '[reconfigure_group] Cannot find the group [%s] in the effective groups, '
                    'keep the original group [%s]',
                    group, self.primehub.primehub_config.current_group.get('name'))
                group_not_found(group)
        else:
            self.primehub.primehub_config.current_group = selected_group

    def _fetch_group_info(self, group):
        query = """
        {
          me {
            effectiveGroups {
              id
              name
              displayName
            }
          }
        }
        """
        results = self.request({}, query)
        for g in results['data']['me']['effectiveGroups']:
            if g['name'] == group:
                return g

    @cmd(name='generate-token', description='Generate Token Flow')
    def generate(self, server_url: str):
        """
        Generate an API token with OAuth authentication flow

        :type server_url: str
        :param server_url: PrimeHub's URL
        """

        flow = OidcAuthenticationFlow(self.primehub)
        flow.generate(_find_oauth_flow_url(server_url))

    def help_description(self):
        return "Update the settings of PrimeHub SDK"


class CliConfig(Config):

    @cmd(name='set-endpoint', description='Set endpoint and save to the config file')
    def set_endpoint(self, endpoint: str):
        """
        Set endpoint to the GraphQL API.

        It usually is in this pattern https://<primehub-domain>/api/graphql

        :type endpoint: str
        :param endpoint: an URL to GraphQL API endpoint
        """
        super(CliConfig, self).set_endpoint(endpoint)
        self.update()

    @cmd(name='set-token', description='Set token and save to the config file')
    def set_token(self, token: str):
        """
        Set api-token to the PrimeHubConfig

        :type token: str
        :param token: a token used by GraphQL request
        """
        super(CliConfig, self).set_token(token)
        self.update()

    @cmd(name='set-group', description='Set group and save to the config file')
    def set_group(self, group: str):
        """
        Set current group to work with group aware actions.

        When setting a group, it will validate the group. It the group is invalid, PrimeHub.current_group will be None.

        :type group: str
        :param group: group name
        """
        super(CliConfig, self).set_group(group)
        if not self.primehub.primehub_config.group_info:
            group_not_found(group)
        if not self.primehub.primehub_config.group_info.get('id', None):
            group_not_found(group)
        self.primehub.primehub_config.group = group
        self.update()

    def update(self):
        self.primehub.primehub_config.save()


class OidcAuthenticationFlow:

    def __init__(self, primehub):
        self.primehub = primehub

    def generate(self, api_token_endpoint: str):
        """
        Generate an API token

        :type api_token_endpoint: str
        :param api_token_endpoint: the api-token service endpoint
        """

        request_url = f'{api_token_endpoint}/request'
        print(f'Go to this URL in the browser {request_url}', file=self.primehub.stdout)
        print('Enter your authorization code:', file=self.primehub.stdout)

        code = input()
        if not code or not code.strip():
            print('Stop the process because the blank code', file=self.primehub.stdout)
            return

        exchange_url = f'{api_token_endpoint}/exchange'
        config_from_console = requests.post(exchange_url, dict(code=code)).text
        if config_from_console == 'Bad Request':
            print('Failed to fetch API Token', file=self.primehub.stderr)
            return

        try:
            data = json.loads(config_from_console)
            if 'api-token' in data:
                self._save_config(config_from_console)
            else:
                print(config_from_console)
        except BaseException:
            raise

    def _generate_new_config(self, config_file_path):
        from primehub import PrimeHubConfig
        cfg = PrimeHubConfig(config=config_file_path)
        self.primehub.primehub_config = cfg

        # pick the first group
        groups = self.primehub.groups.list()
        if groups:
            cfg.group = groups[0]['name']

        default_config_path = os.path.expanduser('~/.primehub/config.json')
        if os.path.exists(default_config_path):
            backup_path = os.path.expanduser(f'~/.primehub/config-{datetime.now().strftime("%Y%m%d%H%M%S")}.json')
            copyfile(default_config_path, backup_path)
            print(f'Found old configuration, backup it to {backup_path}')

        cfg.save(default_config_path)
        print(f'PrimeHub SDK Config has been updated: {default_config_path}', file=self.primehub.stdout)

    def _save_config(self, config_from_console: str):
        config_file_path = self._save_tmp_config(config_from_console)
        origin_config = self.primehub.primehub_config
        try:
            self._generate_new_config(config_file_path)
        except Exception:
            raise
        finally:
            self.primehub.primehub_config = origin_config

    def _save_tmp_config(self, config_from_console):
        fd, config_file_path = tempfile.mkstemp('.json', '.primehub-sdk')
        with open(config_file_path, "w") as fh:
            fh.write(config_from_console)
        return config_file_path


def _make_possible_urls(server_url: str):
    p = urlparse(server_url)
    base_url = f'{p.scheme}://{p.netloc}'
    return [f'{base_url}/oidc/auth-flow', f'{base_url}/console/oidc/auth-flow']
    return server_url


def _find_oauth_flow_url(server_url: str):
    urls = _make_possible_urls(server_url)
    for base_url in urls:
        try:
            response = requests.head(f'{base_url}/request', timeout=3)
            if response.status_code == 302:
                return f'{base_url}'
        except BaseException:
            pass

    raise ValueError(f'Cannot find the oauth-flow service from {server_url}')


if __name__ == '__main__':
    _find_oauth_flow_url('http://127.0.0.1:3000')
