from primehub.admin_groups import validate, validate_cpu_resource, validate_gpu_resource, validate_memory_resource
from primehub.admin_groups import validate_model_deployment, validate_shared_volume, validate_admins, validate_users
from primehub.utils import PrimeHubException
from tests import BaseTestCase


class TestAdminUsers(BaseTestCase):

    def setUp(self) -> None:
        super(TestAdminUsers, self).setUp()

    def check_exception(self, cfg: dict, message: str, callback=None):
        with self.assertRaises(PrimeHubException) as context:
            if callback is None:
                validate(cfg)
            else:
                callback(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def test_required_field_validator(self):

        # check empty name
        self.check_exception({}, 'name is required')

        # check invalid name
        self.check_exception(
            {'name': 'a'}, 'Group name must begin and end with an alphanumeric character.')
        self.check_exception(
            {'name': '^_^'}, 'Group name must begin and end with an alphanumeric character.')

        # pass with valid configuration
        validate({'name': 'my-group-1'})
        validate({'name': '123-group'})
        validate({'name': 'aaaAAA'})
        validate({'name': 'AAAaaa'})

    def test_cpu_memory_gpu_validator(self):

        # check invalid user quota
        self.check_exception(
            {'quotaCpu': -1.5}, 'quotaCpu should be non-negative value', validate_cpu_resource)
        self.check_exception(
            {'quotaCpu': -1}, 'quotaCpu should be non-negative value', validate_cpu_resource)
        self.check_exception(
            {'quotaCpu': '1'}, "quotaCpu should be a value in ['float', 'int'] types", validate_cpu_resource)

        self.check_exception(
            {'quotaGpu': -1.5}, "quotaGpu should be a value in ['int'] types", validate_gpu_resource)
        self.check_exception(
            {'quotaGpu': -1}, 'quotaGpu should be non-negative value', validate_gpu_resource)
        self.check_exception(
            {'quotaGpu': 1.5}, "quotaGpu should be a value in ['int'] types", validate_gpu_resource)

        self.check_exception(
            {'quotaMemory': -1.5}, 'quotaMemory should be non-negative value', validate_memory_resource)
        self.check_exception(
            {'quotaMemory': -1}, 'quotaMemory should be non-negative value', validate_memory_resource)

        # check invalid group quota
        self.check_exception({'projectQuotaCpu': -1.5},
                             'projectQuotaCpu should be non-negative value', validate_cpu_resource)
        self.check_exception(
            {'projectQuotaCpu': -1}, 'projectQuotaCpu should be non-negative value', validate_cpu_resource)

        self.check_exception(
            {'projectQuotaGpu': -1}, 'projectQuotaGpu should be non-negative value', validate_gpu_resource)
        self.check_exception(
            {'projectQuotaGpu': 1.5}, "projectQuotaGpu should be a value in ['int'] types", validate_gpu_resource)

        self.check_exception({'projectQuotaMemory': -1.5},
                             'projectQuotaMemory should be non-negative value', validate_memory_resource)
        self.check_exception({'projectQuotaMemory': -1},
                             'projectQuotaMemory should be non-negative value', validate_memory_resource)

        # check invalid user and group quota
        self.check_exception({'quotaCpu': 1, 'projectQuotaCpu': 0.5},
                             'quotaCpu less than or equal to projectQuotaCpu', validate_cpu_resource)

        self.check_exception({'quotaGpu': 2, 'projectQuotaGpu': 1},
                             'quotaGpu less than or equal to projectQuotaGpu', validate_gpu_resource)

        self.check_exception({'quotaMemory': 2, 'projectQuotaMemory': 1.5},
                             'quotaMemory less than or equal to projectQuotaMemory', validate_memory_resource)

        # pass with valid user quota
        validate_cpu_resource({'quotaCpu': 0.5})
        validate_cpu_resource({'quotaCpu': 1})
        validate_gpu_resource({'quotaGpu': 0})
        validate_gpu_resource({'quotaGpu': 1})
        validate_memory_resource({'quotaMemory': 0.5})
        validate_memory_resource({'quotaMemory': 1})

        # pass with valid group quota
        validate_cpu_resource({'projectQuotaCpu': 0.5})
        validate_cpu_resource({'projectQuotaCpu': 1})
        validate_gpu_resource({'projectQuotaGpu': 0})
        validate_gpu_resource({'projectQuotaGpu': 1})
        validate_memory_resource({'projectQuotaMemory': 0.5})
        validate_memory_resource({'projectQuotaMemory': 1})

        # pass with valid user and group combination

        validate_cpu_resource({'quotaCpu': 1, 'projectQuotaCpu': 1})
        validate_gpu_resource({'quotaGpu': 2, 'projectQuotaGpu': 3})
        validate_memory_resource({'quotaMemory': 2, 'projectQuotaMemory': 2.5})

    def test_model_deployment_validator(self):

        # check invalid model deployment
        self.check_exception({'enabledDeployment': 1},
                             'enabledDeployment should be bool value', validate_model_deployment)
        self.check_exception({'enabledDeployment': False, 'maxDeploy': 1},
                             'enabledDeployment should be set for maxDeploy', validate_model_deployment)
        self.check_exception({'enabledDeployment': True, 'maxDeploy': 1.5},
                             'maxDeploy should be integer value', validate_model_deployment)
        self.check_exception({'enabledDeployment': True, 'maxDeploy': -1},
                             'maxDeploy should be non-negative value', validate_model_deployment)

        # pass with valid model deployment
        validate_model_deployment({'enabledDeployment': False})
        validate_model_deployment({'enabledDeployment': True})
        validate_model_deployment({'enabledDeployment': True, 'maxDeploy': 0})
        validate_model_deployment({'enabledDeployment': True, 'maxDeploy': 1})

    def test_shared_volume_validator(self):

        # check invalid shared volume
        self.check_exception({'enabledSharedVolume': 1},
                             'enabledSharedVolume should be bool value', validate_shared_volume)
        self.check_exception({'enabledSharedVolume': False, 'sharedVolumeCapacity': 1},
                             'enabledSharedVolume should be set for sharedVolumeCapacity', validate_shared_volume)
        self.check_exception({'enabledSharedVolume': False, 'launchGroupOnly': False},
                             'enabledSharedVolume should be set for launchGroupOnly', validate_shared_volume)
        self.check_exception({'enabledSharedVolume': True, 'sharedVolumeCapacity': 1.5, 'launchGroupOnly': 1},
                             'sharedVolumeCapacity should be integer value', validate_shared_volume)
        self.check_exception({'enabledSharedVolume': True, 'sharedVolumeCapacity': -1, 'launchGroupOnly': 1},
                             'sharedVolumeCapacity should be non-negative value', validate_shared_volume)
        self.check_exception({'enabledSharedVolume': True, 'sharedVolumeCapacity': 1, 'launchGroupOnly': 1},
                             'launchGroupOnly should be bool value', validate_shared_volume)

        # pass with valid shared volume
        validate_shared_volume({'enabledSharedVolume': False})
        validate_shared_volume({'enabledSharedVolume': True})
        validate_shared_volume(
            {'enabledSharedVolume': True, 'sharedVolumeCapacity': 0})
        validate_shared_volume(
            {'enabledSharedVolume': True, 'launchGroupOnly': False})
        validate_shared_volume(
            {'enabledSharedVolume': True, 'sharedVolumeCapacity': 1, 'launchGroupOnly': True})

    def test_admins_users_validator(self):

        # check invalid admin
        self.check_exception(
            {'admins': 123}, 'admins should be string type', validate_admins)

        # check invalid users connection
        self.check_exception({'users': {'connect': [{'name': 'user1'}, {'name': 'user2'}], 'disconnect': []}},
                             'users connection payload should be an entry {id}', validate_users)
        self.check_exception({'users': {'connect': [{'id': '123', 'name': 'user1'}], 'disconnect': []}},
                             'users connection payload should be an entry {id}', validate_users)
        self.check_exception({'users': {'connect': [], 'disconnect': [{'name': 'user1'}, {'name': 'user2'}]}},
                             'users disconnection payload should be an entry {id}', validate_users)

        # pass with valid admin
        validate_admins({'admin': 'test_user_1'})

        # pass with valid users connection
        validate_users({'users': {'connect': [{'id': 'xxx-yyy'}, {'id': 'xxx-zzz'}], 'disconnect': []}})
        validate_users({'users': {'connect': [], 'disconnect': [{'id': 'xxx-yyy'}, {'id': 'xxx-zzz'}]}})
