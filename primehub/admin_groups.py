import json
import re
from typing import Iterator, Union, Any

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag
from primehub.utils.validator import validate_connection


def invalid_config(message: str):
    example = """
    {"name": "group_name", "displayName": "", "enabledDeployment": false, "enabledSharedVolume": false,
    "quotaCpu": 0.5, "quotaGpu": 0, "quotaMemory": null, "projectQuotaCpu": null, "projectQuotaGpu": null,
    "projectQuotaMemory": null, "admins": "", "users": {"connect": [{"id": "user1_id"}, {"id": "user2_id"}]}}
    """.strip()

    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def validate_name(data: dict):
    if 'name' not in data:
        raise PrimeHubException('name is required')

    matched: Union[str, Any, None] = re.match(
        r'^[A-Za-z0-9][-\w]*[A-Za-z0-9]+$',
        data.get('name'))

    # check formats
    if not matched:
        raise PrimeHubException(
            'Group name must begin and end with an alphanumeric character.')


def validate_model_deployment(data: dict):
    flag = 'enabledDeployment'
    depends = [dict(key='maxDeploy', type=int)]
    validate_depends_fields(data, flag, depends)


def validate_shared_volume(data: dict):
    flag = 'enabledSharedVolume'
    depends = [dict(key='sharedVolumeCapacity', type=int), dict(key='launchGroupOnly', type=bool)]
    validate_depends_fields(data, flag, depends)


def validate_depends_fields(data: dict, flag: str, depends: list):
    depends_result = [(x['key'], data.get(x['key']) is not None, data.get(x['key']), x['type']) for x in depends]
    is_enabled = data.get(flag, False)

    # validate flag type
    if not isinstance(is_enabled, bool):
        raise PrimeHubException(f'{flag} should be bool value')

    # check options should not set, when flag is not enabled
    if not is_enabled:
        for field_name, has_value, _, _ in depends_result:
            if has_value:
                raise PrimeHubException(
                    f'{flag} should be set for {field_name}')
        return

    # check options with pre-condition when it has a value
    for field_name, has_value, value, value_type in depends_result:
        if not has_value:
            continue
        if not isinstance(value, value_type):
            raise PrimeHubException(
                f'{field_name} should be {value_type.__name__} value')
        if value_type == int and value < 0:
            raise PrimeHubException(
                f'{field_name} should be non-negative value')


def validate_cpu_resource(data: dict):
    validate_resource_type(data, 'quotaCpu', 'projectQuotaCpu', [float, int])


def validate_memory_resource(data: dict):
    validate_resource_type(data, 'quotaMemory', 'projectQuotaMemory', [float, int])


def validate_gpu_resource(data: dict):
    validate_resource_type(data, 'quotaGpu', 'projectQuotaGpu', [int])


def validate_resource_type(data: dict, user_field: str, project_field: str, acceptable_types: list):
    user_quota = data.get(f'{user_field}', None)
    group_quota = data.get(f'{project_field}', None)
    acceptable_type_names = [x.__name__ for x in acceptable_types]

    # check type
    if user_quota is not None:
        if True not in [isinstance(user_quota, x) for x in acceptable_types]:
            raise PrimeHubException(f'{user_field} should be a value in {acceptable_type_names} types')
        if user_quota < 0:
            raise PrimeHubException(f'{user_field} should be non-negative value')

    if group_quota is not None:
        if True not in [isinstance(group_quota, x) for x in acceptable_types]:
            raise PrimeHubException(f'{project_field} should be a value in {acceptable_type_names} types')
        if group_quota < 0:
            raise PrimeHubException(
                f'{project_field} should be non-negative value')

    # check limit
    if user_quota is not None and group_quota is not None:
        if user_quota > group_quota:
            raise PrimeHubException(
                f'{user_field} less than or equal to {project_field}')


def validate_admins(data: dict):
    admins = data.get('admins', '')

    if not isinstance(admins, str):
        raise PrimeHubException('admins should be string type')


def validate_users(data: dict):
    validate_connection(data, 'users')


def validate(data: dict, for_update: bool = False) -> dict:
    if not for_update:
        validate_name(data)
    else:
        if 'name' in data:
            data.pop('name')

    validate_model_deployment(data)
    validate_shared_volume(data)

    validate_cpu_resource(data)
    validate_gpu_resource(data)
    validate_memory_resource(data)

    validate_admins(data)
    validate_users(data)

    return data


class AdminGroups(Helpful, Module):

    @cmd(name='create', description='Create a group', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Create a group

        :type file: str
        :param file: the file path of the configurations

        :rtype: dict
        :return: the created group
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('The configuration is required.')

        return self.create(config)

    def create(self, config: dict):
        """
        Create a group

        :type config: dict
        :param config: the configurations of the created group

        :rtype: dict
        :return: the created group
        """

        query = """
        mutation CreateGroup($data: GroupCreateInput!) {
          createGroup(data: $data) {
            ...GroupBasicInfo
          }
        }
        fragment GroupBasicInfo on Group {
          id
          displayName
          name
          admins
          quotaCpu
          quotaGpu
          quotaMemory
          projectQuotaCpu
          projectQuotaGpu
          projectQuotaMemory
          sharedVolumeCapacity
        }
        """

        results = self.request({'data': validate(config)}, query)

        if 'data' not in results:
            return results
        return results['data']['createGroup']

    @cmd(name='list', description='List groups', return_required=True, optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator:
        """
        List groups

        :type page: int
        :param page: the page of all data

        :rtype: Iterator
        :return: groups iterator
        """

        query = """
        query GroupsConnection(
          $page: Int
          $orderBy: GroupOrderByInput
          $where: GroupWhereInput
        ) {
          group: groupsConnection(page: $page, orderBy: $orderBy, where: $where) {
            edges {
              cursor
              node {
                ...GroupBasicInfo
              }
            }
            pageInfo {
              currentPage
              totalPage
            }
          }
        }
        fragment GroupBasicInfo on Group {
          id
          displayName
          name
          admins
          quotaCpu
          quotaGpu
          quotaMemory
          projectQuotaCpu
          projectQuotaGpu
          projectQuotaMemory
          sharedVolumeCapacity
        }
        """

        variables: dict = {'orderBy': {}, 'where': {}}
        page = kwargs.get('page', 0)
        if page > 0:
            variables['page'] = page
            results = self.request(variables, query)
            for e in results['data']['group']['edges']:
                yield e['node']
            return

        page = 1
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['group']['edges']:
                for e in results['data']['group']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    @cmd(name='get', description='Get the group info by id', return_required=True)
    def get(self, id: str) -> dict:
        """
        Get the group info by id

        :type id: str
        :param id: the group id

        :rtype: dict
        :return: the group info
        """

        query = """
        query Group(
          $where: GroupWhereUniqueInput!
          $everyoneGroupWhere: GroupWhereUniqueInput!
        ) {
          group(where: $where) {
            ...GroupInfo
          }
          everyoneGroup: group(where: $everyoneGroupWhere) {
            ...GroupResourceInfo
          }
        }
        fragment GroupInfo on Group {
          id
          displayName
          name
          admins
          users {
            id
            username
          }
          quotaCpu
          quotaGpu
          quotaMemory
          projectQuotaCpu
          projectQuotaGpu
          projectQuotaMemory
          resourceStatus {
            cpuUsage
            memUsage
            gpuUsage
          }
          enabledDeployment
          maxDeploy
          deploymentsUsage
          enabledSharedVolume
          jobDefaultActiveDeadlineSeconds
          sharedVolumeCapacity
          launchGroupOnly
          ...GroupResourceInfo
        }
        fragment GroupResourceInfo on Group {
          datasets {
            id
            displayName
            description
            writable
            type
          }
          images {
            id
            displayName
            type
            description
          }
          instanceTypes {
            id
            displayName
            description
            cpuLimit
            gpuLimit
            memoryLimit
          }
        }
        """

        variables = {'where': {'id': id}, 'everyoneGroupWhere': {
            'id': self._everyone_group_id()}}
        results = self.request(variables, query)

        if 'data' not in results:
            return results

        return results['data']['group']

    def _everyone_group_id(self) -> dict:
        query = """
        query {
          me {
            groups {
              id
              name
            }
          }
        }
        """
        results = self.request({}, query)
        if 'data' in results:
            for group in results['data']['me']['groups']:
                if group['name'] == 'everyone':
                    return group['id']

        raise PrimeHubException('cannot find the everyone group id')

    @cmd(name='update', description='Update the group', optionals=[('file', file_flag)])
    def _update_cmd(self, id: str, **kwargs):
        """
        Update the group

        :type id: str
        :param id: the group id
        :type file: str
        :param file: the file path of the configurations

        :rtype: dict
        :return: the updated group
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('The configuration is required.')

        return self.update(id, config)

    def update(self, id: str, config: dict):
        """
        Update the group

        :type id: str
        :param id: the group id
        :type config: dict
        :param config: the configurations for the updated group

        :rtype: dict
        :return: the group
        """

        query = """
        mutation UpdateGroup($data: GroupUpdateInput!, $where: GroupWhereUniqueInput!) {
          updateGroup(data: $data, where: $where) {
            ...GroupBasicInfo
          }
        }
        fragment GroupBasicInfo on Group {
          id
          displayName
          name
          admins
          quotaCpu
          quotaGpu
          quotaMemory
          projectQuotaCpu
          projectQuotaGpu
          projectQuotaMemory
          sharedVolumeCapacity
        }
        """
        variables = {'where': {'id': id}, 'data': validate(config, True)}
        results = self.request(variables, query)

        if 'data' not in results:
            return results
        return results['data']['updateGroup']

    @cmd(name='delete', description='Delete the group by id', return_required=True)
    def delete(self, id: str) -> dict:
        """
        Delete the group by id

        :type id: str
        :param id: the group id

        :rtype: dict
        :return: the deleted group
        """

        query = """
        mutation DeleteGroup($where: GroupWhereUniqueInput!) {
          deleteGroup(where: $where) {
            id
          }
        }
        """

        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results
        return results['data']['deleteGroup']

    def help_description(self):
        return "Manage groups"
