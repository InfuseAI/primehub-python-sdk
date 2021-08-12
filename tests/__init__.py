import functools
import io
import json
import os
from unittest import TestCase, mock

from primehub import PrimeHub, PrimeHubConfig, cli
from primehub.utils import create_logger

logger = create_logger('primehub-test')


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
        print("the default path is ", self.test_default_config_path)

        self.sdk = PrimeHub(PrimeHubConfig())
        self.sdk.stderr = io.StringIO()
        self.sdk.stdout = io.StringIO()

    def tearDown(self) -> None:
        os.environ['PRIMEHUB_GROUP'] = ""
        os.environ['PRIMEHUB_API_TOKEN'] = ""
        os.environ['PRIMEHUB_API_ENDPOINT'] = ""

    @reset_stderr_stdout
    def cli_stderr(self, argv: list):
        print("cli_stderr", argv)
        self.invoke_cli(argv)
        return self.sdk.stderr.getvalue()

    @reset_stderr_stdout
    def cli_stdout(self, argv: list):
        print("cli_stdout", argv)
        self.invoke_cli(argv)
        return self.sdk.stdout.getvalue()

    def invoke_cli(self, argv: list):
        try:
            import sys
            sys.argv = argv
            if [x for x in argv if not isinstance(x, str)]:
                raise ValueError('all arguments must be a str type')
            if '--json' not in sys.argv:
                sys.argv.append('--json')
            cli.main(sdk=self.sdk)
        except SystemExit:
            pass

    def reset_cli_output(self):
        logger.info("\n{} reset_cli_output {}".format("=" * 40, "=" * 40))
        logger.info("\nSTDOUT:\n\n{}\n\nSTDERR:\n\n{}\n\n".format(self.sdk.stdout.getvalue(),
                                                                  self.sdk.stderr.getvalue()))
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

    def assert_config_with_prefix(self, prefix: str, cfg: PrimeHubConfig):
        self.assertEqual(prefix + ':endpoint', cfg.endpoint)
        self.assertEqual(prefix + ':api-token', cfg.api_token)
        self.assertEqual(cfg.current_group.get('name'), cfg.group)
        self.assertEqual(prefix + ':group', cfg.current_group.get('name'))

    def tempfile(self):
        from tempfile import mkstemp
        fd, p = mkstemp(".data", text=True)
        return p

    def load_json_file(self, path):
        with open(path, "r") as fh:
            return json.load(fh)
