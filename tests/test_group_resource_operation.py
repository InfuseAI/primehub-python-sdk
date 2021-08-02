import json

from primehub import Module, cmd, Helpful
from primehub.resource_operations import GroupResourceOperation
from tests import BaseTestCase


class GroupFoobarCommand(Helpful, Module, GroupResourceOperation):

    def help_description(self):
        return "foo bar"

    @cmd(name='list', description='')
    def list(self):
        return self.do_list('fake-query', 'foobar')

    @cmd(name='get', description='')
    def get(self, name):
        return self.do_get('fake-query', 'foobar', name)


class TestGroupResourceOperation(BaseTestCase):

    def setUp(self) -> None:
        super(TestGroupResourceOperation, self).setUp()
        self.sdk.register_command('test_group_resource_operation', GroupFoobarCommand)

    def test_group_not_found(self):
        output = self.cli_stderr(['app.py', 'test_group_resource_operation', 'list'])
        self.assertEqual('No group information, please configure the active group first.', output.strip())

    def test_group_resource_operation(self):
        self.sdk.primehub_config.group_info = {'name': 'phusers', 'id': 'any-id'}
        self.mock_request.return_value = {
            'data': {
                'me': {
                    'effectiveGroups': [
                        {'name': 'group-1', 'foobar': [dict(name="1", value="1")]},
                        {'name': 'group-2', 'foobar': [dict(name="2", value="2")]},
                        {'name': 'phusers', 'foobar': [dict(name="3", value="3")]},
                    ]
                }
            }
        }

        # verify list will select the right group
        output = self.cli_stdout(['app.py', 'test_group_resource_operation', 'list'])
        self.assertEqual([dict(name="3", value="3")], json.loads(output))

        # verify get by name
        output = self.cli_stdout(['app.py', 'test_group_resource_operation', 'get', '3'])
        self.assertEqual(dict(name="3", value="3"), json.loads(output))
