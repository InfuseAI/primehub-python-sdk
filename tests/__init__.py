import functools
import io
import json
import os
from unittest import TestCase, mock

from primehub import PrimeHub, PrimeHubConfig, cli


def reset_stderr_stdout(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            args[0].reset_cli_output()

    return wrapper


class BaseTestCase(TestCase):
    """
    A base test case which mocks out the low-level HTTP Client to prevent
    any actual calls to the API.
    """

    def setUp(self) -> None:

        import primehub.utils.http_client

        primehub.utils.http_client.Client.request = mock.MagicMock()
        self.mock_request = primehub.utils.http_client.Client.request

        import primehub
        self.test_default_config_path = self.tempfile()
        primehub.PrimeHubConfig.get_default_path = mock.MagicMock()
        primehub.PrimeHubConfig.get_default_path.return_value = self.test_default_config_path

        self.sdk = PrimeHub(PrimeHubConfig())
        self.sdk.stderr = io.StringIO()
        self.sdk.stdout = io.StringIO()

    def tearDown(self) -> None:
        os.environ['PRIMEHUB_GROUP'] = ""
        os.environ['PRIMEHUB_API_TOKEN'] = ""
        os.environ['PRIMEHUB_API_ENDPOINT'] = ""

    @reset_stderr_stdout
    def cli_stderr(self, argv: list):
        try:
            import sys
            sys.argv = argv
            cli.main(sdk=self.sdk)
        except SystemExit:
            pass
        return self.sdk.stderr.getvalue()

    @reset_stderr_stdout
    def cli_stdout(self, argv: list):
        try:
            import sys
            sys.argv = argv
            cli.main(sdk=self.sdk)
        except SystemExit:
            pass
        return self.sdk.stdout.getvalue()

    def reset_cli_output(self):
        self.sdk.stderr = io.StringIO()
        self.sdk.stdout = io.StringIO()

    def create_fake_config(self, content: dict) -> str:
        from tempfile import mkstemp
        fd, p = mkstemp('.json', text=True)
        with open(p, "w") as fh:
            fh.write(json.dumps(content))
        return p

    def create_config_dict(self, endpoint, token, group):
        return {'endpoint': endpoint, 'api-token': token, 'group': dict(name=group)}

    def cfg_dict_with_prefix(self, prefix: str):
        return self.create_config_dict(prefix + ":endpoint", prefix + ":api-token", prefix + ":group")

    def assert_config_with_prefix(self, prefix: str, cfg):
        self.assertEqual(prefix + ':endpoint', cfg.endpoint)
        self.assertEqual(prefix + ':api-token', cfg.api_token)
        self.assertEqual(prefix + ':group', cfg.group)

    def tempfile(self):
        from tempfile import mkstemp
        fd, p = mkstemp(".data", text=True)
        return p

    def load_json_file(self, path):
        with open(path, "r") as fh:
            return json.load(fh)
