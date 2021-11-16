from primehub.admin_volumes import validate, validate_creation
from primehub.utils import PrimeHubException
from tests import BaseTestCase


class TestVolumes(BaseTestCase):

    def setUp(self) -> None:
        super(TestVolumes, self).setUp()

    def check_required(self, input: dict, message: str):
        with self.assertRaises(PrimeHubException) as context:
            validate(input)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def test_validator(self):
        # check required fields
        self.check_required({}, 'name is required')
        self.check_required({'name': 'volume-name'}, 'type is required')

        # check formats
        self.check_required({'name': '-name', 'type': 'pv'},
                            "[name] should be lower case alphanumeric characters, '-' or '.', "
                            "and must start and end with an alphanumeric character.")

        self.check_required({'name': 'name', 'type': 'whatever'},
                            "[type] should be one of ['pv', 'nfs', 'hostPath', 'git', 'env']")

        # check writable groups
        self.check_required({'name': 'name', 'type': 'git', 'enableUploadServer': False},
                            "[enableUploadServer] only can use with should be one of ['pv', 'nfs', 'hostPath'] types")

        # check groups connect/disconnect
        self.check_required({'name': 'name', 'type': 'pv', 'groups': {'connect': [{'name': 'my-group'}]}},
                            "group connect should be a pair {id, writable}")

        self.check_required(
            {'name': 'name', 'type': 'pv', 'groups': {'disconnect': [{'id': 'my-id', 'writable': True}]}},
            "disconnect connect should be an entry {id}")

    def check_creation_required(self, input: dict, message: str):
        with self.assertRaises(PrimeHubException) as context:
            validate_creation(input)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def test_pv_create_validator(self):
        # check required fields
        self.check_creation_required({'name': 'name', 'type': 'pv'},
                                     "pvProvisioning is required for pv type "
                                     "and its value should be one of ['auto', 'manual']")

        self.check_creation_required({'name': 'name', 'type': 'pv', 'pvProvisioning': 'no-such-way'},
                                     "pvProvisioning is required for pv type "
                                     "and its value should be one of ['auto', 'manual']")

        valid_input = {'name': 'name', 'type': 'pv', 'pvProvisioning': 'auto'}
        self.assertEqual(valid_input, validate_creation(valid_input))

    def test_nfs_create_validator(self):
        # check required fields
        self.check_creation_required({'name': 'name', 'type': 'nfs'},
                                     "nfsServer and nfsPath are required for nfs type")

        self.check_creation_required({'name': 'name', 'type': 'nfs', 'nfsServer': '127.0.0.1'},
                                     "nfsServer and nfsPath are required for nfs type")

        valid_input = {'name': 'name', 'type': 'nfs', 'nfsServer': '127.0.0.1', 'nfsPath': '/data'}
        self.assertEqual(valid_input, validate_creation(valid_input))

    def test_hostPath_create_validator(self):
        # check required fields
        self.check_creation_required({'name': 'name', 'type': 'hostPath'},
                                     "hostPath is required for hostPath type")

        valid_input = {'name': 'name', 'type': 'hostPath', 'hostPath': '/data'}
        self.assertEqual(valid_input, validate_creation(valid_input))

    def test_git_create_validator(self):
        # check required fields
        self.check_creation_required({'name': 'name', 'type': 'git'},
                                     "url is required for git type")

        valid_input = {'name': 'name', 'type': 'git', 'url': 'https://github.com/InfuseAI/primehub-python-sdk'}
        self.assertEqual(valid_input, validate_creation(valid_input))
