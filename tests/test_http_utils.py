from types import GeneratorType

from primehub import Client
from tests import BaseTestCase


class TestHttpRequestLogs(BaseTestCase):

    def setUp(self) -> None:
        super(TestHttpRequestLogs, self).setUp()

    def test_request_logs(self):
        url = 'https://github.com/InfuseAI/primehub-python-sdk'
        c = Client(self.sdk.primehub_config)

        # with follow
        g = c.request_logs(url, True, 0)
        self.assertIsInstance(g, GeneratorType)
        count = 0
        for x in g:
            count = count + 1
        self.assertTrue(count > 1, 'Generator gives lots of lines')

        # no follow
        g = c.request_logs(url, False, 0)
        self.assertIsInstance(g, GeneratorType)
        count = 0
        for x in g:
            count = count + 1
        self.assertTrue(count > 1, 'Generator gives lots of lines')
