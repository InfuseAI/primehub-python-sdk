import json
from tests import BaseTestCase


class TestCmdMe(BaseTestCase):
    """
    Usage:
      primehub me [command]

    Show user account

    Available Commands:
      me                   Get user information
    """

    def setUp(self) -> None:
        super(TestCmdMe, self).setUp()

    def test_me(self):
        # me will return anything from the query
        # query {
        #   me {
        #     id
        #     username
        #     firstName
        #     lastName
        #     email
        #     isAdmin
        #   }
        # }
        body = {'id': 'id', 'username': 'username',
                'firstName': 'firstName', 'lastName': 'lastName',
                'email': 'email', 'isAdmin': True}
        self.mock_request.return_value = {'data': {
            'me': body}}
        output = self.cli_stdout(['app.py', 'me'])

        self.assertEqual(body, json.loads(output))
