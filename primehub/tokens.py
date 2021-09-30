import json
import os
import requests
import tempfile
from datetime import datetime
from shutil import copyfile

from primehub import Helpful, cmd, Module, PrimeHubConfig


class TokenManager(Helpful, Module):

    @cmd(name='generate-token', description='Generate Token Flow')
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

    def help_description(self):
        return "Manage the api-token"
