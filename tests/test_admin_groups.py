from primehub.admin_groups import validate, validate_cpu_resource, validate_gpu_resource, validate_memory_resource
from primehub.admin_groups import validate_model_deployment, validate_shared_volume, validate_admins, validate_users
from primehub.admin_groups import requirement_field_type, requirement_field_ge_zero
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
            {'quotaCpu': -1.5}, requirement_field_ge_zero('quotaCpu'), validate_cpu_resource)
        self.check_exception(
            {'quotaCpu': -1}, requirement_field_ge_zero('quotaCpu'), validate_cpu_resource)
        self.check_exception(
            {'quotaCpu': '1'}, requirement_field_type('quotaCpu', 'float, int'), validate_cpu_resource)

        self.check_exception(
            {'quotaGpu': -1.5}, requirement_field_type('quotaGpu', 'int'), validate_gpu_resource)
        self.check_exception(
            {'quotaGpu': -1}, requirement_field_ge_zero('quotaGpu'), validate_gpu_resource)
        self.check_exception(
            {'quotaGpu': 1.5}, requirement_field_type('quotaGpu', 'int'), validate_gpu_resource)

        self.check_exception(
            {'quotaMemory': -1.5}, requirement_field_ge_zero('quotaMemory'), validate_memory_resource)
        self.check_exception(
            {'quotaMemory': -1}, requirement_field_ge_zero('quotaMemory'), validate_memory_resource)

        # check invalid group quota
        self.check_exception(
            {'projectQuotaCpu': -1.5}, requirement_field_ge_zero('projectQuotaCpu'), validate_cpu_resource)
        self.check_exception(
            {'projectQuotaCpu': -1}, requirement_field_ge_zero('projectQuotaCpu'), validate_cpu_resource)

        self.check_exception(
            {'projectQuotaGpu': -1}, requirement_field_ge_zero('projectQuotaGpu'), validate_gpu_resource)
        self.check_exception(
            {'projectQuotaGpu': 1.5}, requirement_field_type('projectQuotaGpu', 'int'), validate_gpu_resource)

        self.check_exception(
            {'projectQuotaMemory': -1.5}, requirement_field_ge_zero('projectQuotaMemory'), validate_memory_resource)
        self.check_exception(
            {'projectQuotaMemory': -1}, requirement_field_ge_zero('projectQuotaMemory'), validate_memory_resource)

        # check invalid user and group quota
        self.check_exception({'quotaCpu': 1, 'projectQuotaCpu': 0.5},
                             'quotaCpu should be less than or equal to projectQuotaCpu', validate_cpu_resource)

        self.check_exception({'quotaGpu': 2, 'projectQuotaGpu': 1},
                             'quotaGpu should be less than or equal to projectQuotaGpu', validate_gpu_resource)

        self.check_exception({'quotaMemory': 2, 'projectQuotaMemory': 1.5},
                             'quotaMemory should be less than or equal to projectQuotaMemory', validate_memory_resource)

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
                             requirement_field_type('enabledDeployment', 'bool'), validate_model_deployment)
        self.check_exception({'enabledDeployment': False, 'maxDeploy': 1},
                             'enabledDeployment should be set for maxDeploy', validate_model_deployment)
        self.check_exception({'enabledDeployment': True, 'maxDeploy': 1.5},
                             requirement_field_type('maxDeploy', 'int'), validate_model_deployment)
        self.check_exception({'enabledDeployment': True, 'maxDeploy': -1},
                             requirement_field_ge_zero('maxDeploy'), validate_model_deployment)

        # pass with valid model deployment
        validate_model_deployment({'enabledDeployment': False})
        validate_model_deployment({'enabledDeployment': True})
        validate_model_deployment({'enabledDeployment': True, 'maxDeploy': 0})
        validate_model_deployment({'enabledDeployment': True, 'maxDeploy': 1})

    def test_shared_volume_validator(self):

        # check invalid shared volume
        self.check_exception({'enabledSharedVolume': 1},
                             requirement_field_type('enabledSharedVolume', 'bool'), validate_shared_volume)
        self.check_exception({'enabledSharedVolume': False, 'sharedVolumeCapacity': 1},
                             'enabledSharedVolume should be set for sharedVolumeCapacity', validate_shared_volume)
        self.check_exception({'enabledSharedVolume': False, 'launchGroupOnly': False},
                             'enabledSharedVolume should be set for launchGroupOnly', validate_shared_volume)
        self.check_exception({'enabledSharedVolume': True, 'sharedVolumeCapacity': 1.5, 'launchGroupOnly': 1},
                             requirement_field_type('sharedVolumeCapacity', 'int'), validate_shared_volume)
        self.check_exception({'enabledSharedVolume': True, 'sharedVolumeCapacity': -1, 'launchGroupOnly': 1},
                             requirement_field_ge_zero('sharedVolumeCapacity'), validate_shared_volume)
        self.check_exception({'enabledSharedVolume': True, 'sharedVolumeCapacity': 1, 'launchGroupOnly': 1},
                             requirement_field_type('launchGroupOnly', 'bool'), validate_shared_volume)

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
            {'admins': 123}, requirement_field_type('admins', 'string'), validate_admins)

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
