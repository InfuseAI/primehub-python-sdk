import os
from tempfile import mkstemp

from primehub import PrimeHubConfig
from tests import BaseTestCase


class TestPrimeHubConfig(BaseTestCase):

    def setUp(self) -> None:
        super(TestPrimeHubConfig, self).setUp()

    def test_primehub_config_evaluation(self):
        endpoint = 'https://example.primehub.io/api/graphql'
        token = 'my-token'
        group = 'my-phusers'

        raw_config = self.create_config_dict(endpoint, token, group)
        default_cfg_path = self.create_fake_config(raw_config)

        class MyPrimeHubConfig(PrimeHubConfig):
            def get_default_path(self):
                return default_cfg_path

        # Verify config from the default path
        cfg = MyPrimeHubConfig()
        self.assertEqual(endpoint, cfg.endpoint)
        self.assertEqual(token, cfg.api_token)
        self.assertEqual(group, cfg.group)

        # Verify config from alternative path
        raw_config['endpoint'] = 'https://different-path.primehub.io'
        alternative_config_file = self.create_fake_config(raw_config)
        cfg = MyPrimeHubConfig(config=alternative_config_file)
        self.assertEqual('https://different-path.primehub.io', cfg.endpoint)
        self.assertEqual(cfg.get_default_path(), default_cfg_path)
        self.assertEqual(cfg.config_file, alternative_config_file)

        # Verify config override by ENV
        os.environ['PRIMEHUB_GROUP'] = 'env:group'
        os.environ['PRIMEHUB_API_TOKEN'] = 'env:api-token'
        os.environ['PRIMEHUB_API_ENDPOINT'] = 'env:endpoint'

        cfg.load_config_from_env()  # force reload env-config
        self.assert_config_with_prefix('env', cfg)

        # Verify override from user
        cfg.endpoint = 'user:endpoint'
        cfg.api_token = 'user:api-token'
        cfg.group = 'user:group'
        self.assert_config_with_prefix('user', cfg)

    def test_primehub_config_save(self):
        endpoint = 'file:endpoint'
        token = 'file:api-token'
        group = 'file:group'

        # Arrange the original configuration file
        raw_config = self.create_config_dict(endpoint, token, group)
        config_file = self.create_fake_config(raw_config)
        cfg = PrimeHubConfig(config=config_file)
        self.assert_config_with_prefix('file', cfg)

        # Assume the user updating the configuration and persist it to the file
        cfg.endpoint = 'save:endpoint'
        cfg.api_token = 'save:api-token'
        cfg.group = 'save:group'

        fd, new_config_path = mkstemp('.json', text=True)
        cfg.save(new_config_path)

        # Verify the new configuration becoming with `save:*` values
        self.assert_config_with_prefix('save', cfg)

    def test_set_from_constructor(self):
        endpoint = 'file:endpoint'
        token = 'file:api-token'
        group = 'file:group'

        # Arrange the original configuration file
        raw_config = self.create_config_dict(endpoint, token, group)
        config_file = self.create_fake_config(raw_config)
        cfg = PrimeHubConfig(config=config_file, endpoint='prop:endpoint')
        self.assertEqual('prop:endpoint', cfg.endpoint)
        self.assertEqual('file:api-token', cfg.api_token)
        self.assertEqual('file:group', cfg.group)
