import json

from tests import BaseTestCase


class TestHttpMocked(BaseTestCase):

    def setUp(self) -> None:
        super(TestHttpMocked, self).setUp()

    def test_mocked_me(self):
        self.mock_request.return_value = {'data': {'me': {'foo': 'barbar'}}}
        self.assertEqual(dict(foo='barbar'), json.loads(self.cli_stdout(['app.py', 'me'])))
