from primehub.jobs import verify_basic_field, verify_timeout
from primehub.jobs import invalid_config
from primehub.utils import PrimeHubException
from tests import BaseTestCase


class TestJobs(BaseTestCase):

    def setUp(self) -> None:
        super(TestJobs, self).setUp()

    def check_exception(self, cfg: dict, message: str, callback=None):
        with self.assertRaises(PrimeHubException) as context:
            if callback is None:
                verify_basic_field(cfg)
            else:
                callback(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def get_exception_message(self, message: str, callback):
        with self.assertRaises(PrimeHubException) as context:
            callback(message)

        return context.exception.args[0]

    def test_basic_field_validator(self):
        # check required fields
        exception_msg = self.get_exception_message('displayName is required', invalid_config)
        self.check_exception({}, exception_msg)

        exception_msg = self.get_exception_message('command is required', invalid_config)
        self.check_exception({'instanceType': 'cpu-1', 'image': 'base-notebook', 'displayName': 'job-example'},
                             exception_msg)

        # check invalid fields
        self.check_exception({'instanceType': 123, 'image': 'base-notebook', 'displayName': 'job-example',
                              'command': 'echo \"great job\"'}, 'instanceType should be string value')

        self.check_exception({'instanceType': 'cpu-1', 'image': '', 'displayName': 'job-example',
                              'command': 'echo \"great job\"'}, 'image should be specified')

        self.check_exception({'instanceType': 'cpu-1', 'image': None, 'displayName': 'job-example',
                              'command': 'echo \"great job\"'}, 'image should be string value')

        # pass with valid config
        verify_basic_field({'instanceType': 'cpu-1', 'image': 'base-notebook', 'displayName': 'job-example',
                            'command': 'echo \"great job\"'})

    def test_timeout_validator(self):
        # check
        self.check_exception({'activeDeadlineSeconds': '86400'}, 'activeDeadlineSeconds should be int value',
                             verify_timeout)
        self.check_exception({'activeDeadlineSeconds': None}, 'activeDeadlineSeconds should not be empty',
                             verify_timeout)

        verify_timeout({'activeDeadlineSeconds': 86400})
