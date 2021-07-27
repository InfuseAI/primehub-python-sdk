import json

from tests import BaseTestCase


class TestHttpMocked(BaseTestCase):

    def setUp(self) -> None:
        super(TestHttpMocked, self).setUp()

    def test_mocked_me(self):
        self.mock_request.return_value = {'data': {'me': {'foo': 'barbar'}}}
        self.assertEqual(dict(foo='barbar'), json.loads(self.cli_stdout(['app.py', 'me'])))


class TestStdoutStderrSideEffect(BaseTestCase):

    def setUp(self) -> None:
        super(TestStdoutStderrSideEffect, self).setUp()

    def test_stdout_stderr_side_effect_removed(self):
        self.mock_request.return_value = {'data': {'me': {'message': 'side-effect'}}}

        output = self.cli_stdout(['app.py', 'me'])
        self.assertEqual({'message': 'side-effect'}, json.loads(output))

        output = self.cli_stdout(['app.py', 'me'])
        self.assertEqual({'message': 'side-effect'}, json.loads(output))

        help1 = self.cli_stderr(['app.py'])
        help2 = self.cli_stderr(['app.py'])
        self.assertEqual(help1, help2)
