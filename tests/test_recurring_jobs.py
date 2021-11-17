from primehub.recurring_jobs import invalid_config
from primehub.recurring_jobs import verify_config, verify_recurrence, verify_recurrence_options
from primehub.utils import PrimeHubException
from tests import BaseTestCase


class TestRecurringJobs(BaseTestCase):

    def setUp(self) -> None:
        super(TestRecurringJobs, self).setUp()

    def check_exception(self, cfg: dict, message: str, callback=None):
        with self.assertRaises(PrimeHubException) as context:
            if callback is None:
                verify_recurrence(cfg)
            else:
                callback(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def get_exception_message(self, message: str, callback):
        with self.assertRaises(PrimeHubException) as context:
            callback(message)

        return context.exception.args[0]

    def test_config_update_validator(self):
        verify_config({'instanceType': 'cpu-1'}, True)
        verify_config({}, True)

    def test_recurrence_validator(self):
        # check required fields
        exception_msg = self.get_exception_message('recurrence is required', invalid_config)
        self.check_exception({}, exception_msg)

        self.check_exception({'recurrence': 'type: daily, cron: 0 4 * * *'}, 'recurrence should be a json object')

        verify_recurrence({'recurrence': {'type': 'custom', 'cron': '0 4 * * *'}})

    def test_recurrence_options_validator(self):
        self.check_exception({'type': 123}, 'type should be string value', verify_recurrence_options)
        self.check_exception({'type': 'my custom'}, '\'my custom\' is not acceptable type', verify_recurrence_options)

        exception_msg = self.get_exception_message('type is required', invalid_config)
        self.check_exception({'cron': '0 4 * * *'}, exception_msg, verify_recurrence_options)
        exception_msg = self.get_exception_message('type is required', invalid_config)
        self.check_exception({'type: '', cron': '0 4 * * *'}, exception_msg, verify_recurrence_options)

        self.check_exception({'type': 'custom', 'cron': 5566}, 'cron should be string value', verify_recurrence_options)
        exception_msg = self.get_exception_message('cron is required in custom type', invalid_config)
        self.check_exception({'type': 'custom'}, exception_msg, verify_recurrence_options)

        verify_recurrence_options({'type': 'on-demand', 'cron': ''})
        verify_recurrence_options({'type': 'weekly', 'cron': ''})
        verify_recurrence_options({'type': 'monthly'})
