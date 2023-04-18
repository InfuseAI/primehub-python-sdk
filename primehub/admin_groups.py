import json
import re
from typing import Dict, Iterator, List, Union, Any

from primehub import HTTPSupport, Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag, toggle_flag
from primehub.utils.validator import validate_connection

group_basic_info = """
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


def invalid_config(message: str):
    example = """
    {"name": "group_name", "displayName": "", "enabledDeployment": false, "enabledSharedVolume": false,
    "quotaCpu": 0.5, "quotaGpu": 0, "quotaMemory": null, "projectQuotaCpu": null, "projectQuotaGpu": null,
    "projectQuotaMemory": null, "admins": "", "users": {"connect": [{"id": "user1_id"}, {"id": "user2_id"}]}}
    """.strip()

    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def requirement_field_type(field_name: str, type_name: str) -> str:
    return f'{field_name} should be a value in {type_name} type'


def requirement_field_ge_zero(field_name: str) -> str:
    return f'{field_name} should be a non-negative value'


def validate_name(data: dict):
    if 'name' not in data:
        raise PrimeHubException('name is required')

    matched: Union[str, Any, None] = None
    name = data.get('name')
    if isinstance(name, str):
        matched = re.match(
            r'^[A-Za-z0-9][-\w]*[A-Za-z0-9]+$',
            name)

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
    def to_entry(x: dict):
        return dict(field_name=x['key'],
                    has_value=data.get(x['key']) is not None,
                    value=data.get(x['key']),
                    type=x['type'])

    requirements = [to_entry(x) for x in depends]
    is_enabled = data.get(flag, False)

    # validate flag type
    if not isinstance(is_enabled, bool):
        raise PrimeHubException(requirement_field_type(flag, 'bool'))

    # check options should not set, when flag is not enabled
    if not is_enabled:
        for entry in requirements:
            if entry.get('has_value'):
                raise PrimeHubException(
                    f'{flag} should be set for {entry.get("field_name")}')
        return

    # check options with pre-condition when it has a value
    for entry in requirements:
        if not entry.get('has_value'):
            continue
        if not isinstance(entry.get('value'), entry.get('type')):
            raise PrimeHubException(requirement_field_type(entry.get('field_name'), entry.get('type').__name__))
        if entry.get('type') == int and entry.get('value') < 0:
            raise PrimeHubException(requirement_field_ge_zero(entry.get('field_name')))


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
            raise PrimeHubException(requirement_field_type(user_field, ', '.join(acceptable_type_names)))
        if user_quota < 0:
            raise PrimeHubException(requirement_field_ge_zero(user_field))

    if group_quota is not None:
        if True not in [isinstance(group_quota, x) for x in acceptable_types]:
            raise PrimeHubException(requirement_field_type(project_field, ', '.join(acceptable_type_names)))
        if group_quota < 0:
            raise PrimeHubException(requirement_field_ge_zero(project_field))

    # check limit
    if user_quota is not None and group_quota is not None:
        if user_quota > group_quota:
            raise PrimeHubException(
                f'{user_field} should be less than or equal to {project_field}')


def validate_admins(data: dict):
    admins = data.get('admins', '')

    if not isinstance(admins, str):
        raise PrimeHubException(requirement_field_type('admins', 'string'))


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


def apply_auto_fill(config: dict):
    if config.get('quotaCpu') is None:
        config['quotaCpu'] = 0.5
    if config.get('quotaGpu') is None:
        config['quotaGpu'] = 0


class AdminGroupsVolumes(HTTPSupport):

    @cmd(name='create-volume', description='Create a new volume and connect it to the group',
         optionals=[('file', file_flag)])
    def _create_volume(self, group_id: str, writable: bool, **kwargs):
        """
        Create a new volume and connect it to the group

        :type group_id: str
        :param group_id: The group id

        :type writable: bool
        :param writable: Set the writable for the connection

        :type file: str
        :param file: The file path of the configurations

        :rtype dict
        :return The instanceType
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            from primehub.admin_volumes import invalid_config as volume_invalid_config
            volume_invalid_config('The configuration is required.')

        return self.create_volume(group_id, writable, config)

    def create_volume(self, group_id: str, writable: bool, config: Dict) -> Dict:
        """
        Create a new volume and connect it to the group

        :type group_id: str
        :param group_id: The group id

        :type writable: bool
        :param writable: Set the writable for the connection

        :type config: dict
        :param config: The configurations for creating an instanceType

        :rtype dict
        :return The volume
        """

        # assign the connected group
        config['global'] = False
        config['groups'] = dict(connect=[dict(id=group_id, writable=writable)])

        return self.primehub.admin.admin_volumes.create(config)

    @cmd(name='disconnect-volume', description='Make the volume leave the group')
    def disconnect_volume(self, group_id: str, volume_id: str) -> Dict:
        """
        Make the volume leave the group

        :type group_id: str
        :param group_id: The group id

        :type volume_id: str
        :param volume_id: The volume id

        :rtype dict
        :return The volume
        """
        return self._volume_group_in_and_out(group_id, volume_id, False)

    @cmd(name='connect-volume', description='Make the volume join the group')
    def connect_volume(self, group_id: str, volume_id: str) -> Dict:
        """
        Make the volume join the group

        :type group_id: str
        :param group_id: The group id

        :type volume_id: str
        :param volume_id: The volume id

        :rtype dict
        :return The volume
        """
        return self._volume_group_in_and_out(group_id, volume_id, True)

    def _volume_group_in_and_out(self, group_id: str, image_id: str, execute_connect: bool):
        query = """
        mutation UpdateVolumeMutation(
          $payload: DatasetUpdateInput!
          $where: DatasetWhereUniqueInput!
        ) {
          updateVolume: updateDataset(data: $payload, where: $where) {
            id
            uploadServerSecret {
              username
              password
            }
          }
        }
        """

        connect = []
        disconnect = []
        group_info = {"id": group_id}

        if execute_connect:
            connect.append(group_info)
        else:
            disconnect.append(group_info)

        variables = {
            "payload": {
                "groups": {
                    "connect": connect,
                    "disconnect": disconnect
                }
            },
            "where": {
                "id": image_id
            }
        }
        results = self.request(variables, query)
        if 'data' not in results:
            return results
        return results['data']['updateVolume']

    @cmd(name='list-volumes', description='List volumes in the group')
    def list_volumes(self, group_id: str) -> List:
        """
        List volumes in the group

        :type group_id: str
        :param group_id: The group id

        :rtype list
        :return volumes list
        """
        results = self.primehub.admin.admin_groups.get(group_id)
        if 'id' not in results or 'volumes' not in results:
            return results
        return results['volumes']


class AdminGroupsInstanceTypes(HTTPSupport):

    @cmd(name='create-instancetype', description='Create a new instanceType and connect it to the group',
         optionals=[('file', file_flag)])
    def _create_instancetype(self, group_id: str, **kwargs):
        """
        Create a new instanceType and connect it to the group

        :type group_id: str
        :param group_id: The group id

        :type file: str
        :param file: The file path of the configurations

        :rtype dict
        :return The instanceType
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            from primehub.admin_instancetypes import invalid_config as instancetype_invalid_config
            instancetype_invalid_config('The configuration is required.')

        return self.create_instancetype(group_id, config)

    def create_instancetype(self, group_id: str, config: Dict) -> Dict:
        """
        Create a new instanceType and connect it to the group

        :type group_id: str
        :param group_id: The group id

        :type config: dict
        :param config: The configurations for creating an instanceType

        :rtype dict
        :return The instanceType
        """

        # assign the connected group
        config['global'] = False
        config['groups'] = dict(connect=[dict(id=group_id)])

        return self.primehub.admin.admin_instancetypes.create(config)

    @cmd(name='disconnect-instancetype', description='Make the instanceType leave the group')
    def disconnect_instancetype(self, group_id: str, instancetype_id: str) -> Dict:
        """
        Make the instanceType leave the group

        :type group_id: str
        :param group_id: The group id

        :type instancetype_id: str
        :param instancetype_id: The instanceType id

        :rtype dict
        :return The image
        """
        return self._instancetype_group_in_and_out(group_id, instancetype_id, False)

    @cmd(name='connect-instancetype', description='Make the instanceType join the group')
    def connect_instancetype(self, group_id: str, instancetype_id: str) -> Dict:
        """
        Make the instanceType join the group

        :type group_id: str
        :param group_id: The group id

        :type instancetype_id: str
        :param instancetype_id: The instanceType id

        :rtype dict
        :return The image
        """
        return self._instancetype_group_in_and_out(group_id, instancetype_id, True)

    def _instancetype_group_in_and_out(self, group_id: str, image_id: str, execute_connect: bool):
        query = """
        mutation UpdateInstanceTypeMutation(
          $payload: InstanceTypeUpdateInput!
          $where: InstanceTypeWhereUniqueInput!
        ) {
          updateInstanceType(data: $payload, where: $where) {
            id
            global
            cpuRequest
            memoryRequest
            groups {
              id
              name
              displayName
              quotaCpu
              quotaGpu
            }
            nodeSelector
          }
        }
        """

        connect = []
        disconnect = []
        group_info = {"id": group_id}

        if execute_connect:
            connect.append(group_info)
        else:
            disconnect.append(group_info)

        variables = {
            "payload": {
                "groups": {
                    "connect": connect,
                    "disconnect": disconnect
                }
            },
            "where": {
                "id": image_id
            }
        }
        results = self.request(variables, query)
        if 'data' not in results:
            return results
        return results['data']['updateInstanceType']

    @cmd(name='list-instancetypes', description='List instanceTypes in the group')
    def list_instancetypes(self, group_id: str) -> List:
        """
        List instance-type in the group

        :type group_id: str
        :param group_id: The group id

        :rtype list
        :return instance-type list
        """
        results = self.primehub.admin.admin_groups.get(group_id)
        if 'id' not in results or 'instanceTypes' not in results:
            return results
        return results['instanceTypes']


class AdminGroupsImages(HTTPSupport):

    @cmd(name='create-image', description='Add the image to the group', optionals=[('file', file_flag)])
    def _create_image(self, group_id: str, **kwargs):
        """
        Create a new image and connect it to a specific group

        :type group_id: str
        :param group_id: The group id

        :type file: str
        :param file: The file path of the configurations

        :rtype dict
        :return The image
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            from primehub.admin_images import invalid_config as image_invalid_config
            image_invalid_config('The configuration is required.')

        return self.create_image(group_id, config)

    def create_image(self, group_id: str, config: Dict) -> Dict:
        """
        Create a new image and connect it to the group

        :type group_id: str
        :param group_id: The group id

        :type config: dict
        :param config: The configurations for creating an image

        :rtype dict
        :return The image
        """

        # assign the connected group
        config['global'] = False
        config['groups'] = dict(connect=[dict(id=group_id)])

        return self.primehub.admin.admin_images.create(config)

    @cmd(name='disconnect-image', description='Make the image leave the group')
    def disconnect_image(self, group_id: str, image_id: str) -> Dict:
        """
        Make the image leave the group

        :type group_id: str
        :param group_id: The group id

        :type image_id: str
        :param image_id: The image id

        :rtype dict
        :return The image
        """
        return self._image_group_in_and_out(group_id, image_id, False)

    @cmd(name='connect-image', description='Make the image join the group')
    def connect_image(self, group_id: str, image_id: str) -> Dict:
        """
        Make the image join the group

        :type group_id: str
        :param group_id: The group id

        :type image_id: str
        :param image_id: The image id

        :rtype dict
        :return The image
        """
        return self._image_group_in_and_out(group_id, image_id, True)

    def _image_group_in_and_out(self, group_id: str, image_id: str, execute_connect: bool):
        query = """
        mutation UpdateImageMutation(
          $data: ImageUpdateInput!
          $where: ImageWhereUniqueInput!
        ) {
          updateImage(data: $data, where: $where) {
            id
            groups {
              id
              name
              displayName
            }
            ...ImageInfo
          }
        }
        fragment ImageInfo on Image {
          id
          displayName
          description
          url
          urlForGpu
          name
          type
          groupName
          useImagePullSecret
          logEndpoint
          isReady
          spec
          global
          jobStatus {
            phase
          }
          imageSpec {
            baseImage
            pullSecret
            packages {
              apt
              conda
              pip
            }
          }
        }
        """

        connect = []
        disconnect = []
        group_info = {"id": group_id}

        if execute_connect:
            connect.append(group_info)
        else:
            disconnect.append(group_info)

        variables = {
            "data": {
                "groups": {
                    "connect": connect,
                    "disconnect": disconnect
                }
            },
            "where": {
                "id": image_id
            }
        }
        results = self.request(variables, query)
        if 'data' not in results:
            return results
        return results['data']['updateImage']

    @cmd(name='list-images', description='List images in the group')
    def list_images(self, group_id: str) -> List:
        """
        List images in the group

        :type group_id: str
        :param group_id: The group id

        :rtype list
        :return image list
        """
        results = self.primehub.admin.admin_groups.get(group_id)
        if 'id' not in results or 'images' not in results:
            return results
        return results['images']


class AdminGroupsUsers(HTTPSupport):

    @cmd(name='connect-user', description='Add the user to the group', optionals=[('enable_group_admin', toggle_flag)])
    def connect_user(self, group_id: str, user_id: str, **kwargs):
        """
        Add the user to the group

        :type group_id: str
        :param group_id: the group id

        :type user_id: str
        :param user_id: the user id

        :returns errors or group-id if the user was added
        :rtype dict
        """

        enable_group_admin = kwargs.get('enable_group_admin', False)
        new_group_admins = None
        if enable_group_admin:
            new_group_admins = self._make_group_admins(group_id, user_id, True)

        query = """
        mutation UpdateGroup($data: GroupUpdateInput!, $where: GroupWhereUniqueInput!) {
          updateGroup(data: $data, where: $where) {
            id
          }
        }
        """

        variables: Dict[str, Any] = {
            "where": {
                "id": group_id
            },
            "data": {
                "users": {
                    "connect": [
                        {
                            "id": user_id
                        }
                    ],
                    "disconnect": []
                }
            }
        }

        if new_group_admins is not None:
            variables['data']['admins'] = new_group_admins

        results = self.request(variables, query)
        if 'data' not in results:
            return results

        # the result will be at results['data']['updateGroup']
        # but we only care if the user was added successfully
        return results['data']['updateGroup']

    @cmd(name='disconnect-user', description='Remove the user from the group',
         optionals=[('disable_group_admin', toggle_flag)])
    def disconnect_user(self, group_id: str, user_id: str, **kwargs):
        """
        Add the user to the group

        :type group_id: str
        :param group_id: the group id

        :type user_id: str
        :param user_id: the user id

        :returns errors or group-id if the user was added
        :rtype dict
        """

        disable_group_admin = kwargs.get('disable_group_admin', False)

        query = """
        mutation UpdateGroup($data: GroupUpdateInput!, $where: GroupWhereUniqueInput!) {
          updateGroup(data: $data, where: $where) {
            id
          }
        }
        """

        group_admins = self._make_group_admins(group_id, user_id, False)
        variables: Dict[str, Any] = {
            "where": {
                "id": group_id
            },
            "data": {
                "users": {
                    "connect": [],
                    "disconnect": [{
                        "id": user_id
                    }]
                }
            }
        }

        if group_admins is not None:
            variables['data']['admins'] = group_admins

        if disable_group_admin:
            # only disable group-admin flag
            del variables['data']['users']

        results = self.request(variables, query)
        if 'data' not in results:
            return results

        # the result will be at results['data']['updateGroup']
        # but we only care if the user was removed successfully
        return results['data']['updateGroup']

    @cmd(name='list-users', description='List users in the group')
    def list_users(self, group_id: str):
        """
        List users in the group

        :type group_id: str
        :param group_id: the group id

        :returns errors or list
        :rtype dict, list
        """

        query = """
        query Group($where: GroupWhereUniqueInput!) {
          group(where: $where) {
            admins
            users {
              id
              username
            }
          }
        }
        """

        variables = {"where": {
            "id": group_id
        }}

        results = self.request(variables, query)
        if 'data' not in results:
            return results

        group_admins = [x.strip() for x in results['data']['group'].get('admins', '').split(',')]

        # decorate the users with group-admin information
        users = results['data']['group']['users']
        for u in users:
            if u['username'] in group_admins:
                u['group_admin'] = True
            else:
                u['group_admin'] = False

        return users

    def _make_group_admins(self, group_id: str, user_id: str, added: bool):
        user_dict = self.primehub.admin.admin_users.get(user_id)
        username = None
        if 'id' in user_dict and 'username' in user_dict:
            username = user_dict['username']

        if username is None:
            # it is not possible to make a new list
            return None

        query = """
        query Group($where: GroupWhereUniqueInput!) {
          group(where: $where) {
            admins
          }
        }
        """

        results = self.request({"where": {"id": group_id}}, query)
        if 'data' not in results:
            return None

        group_admins = [x.strip() for x in results['data']['group'].get('admins', '').split(',')]

        if added:
            # add the user to the group admin list
            if username not in group_admins:
                group_admins.append(username)
        else:
            # remove the user from the group admin list
            if username in group_admins:
                group_admins.remove(username)

        return ",".join(group_admins)


class AdminGroups(Helpful, Module,
                  AdminGroupsUsers, AdminGroupsImages,
                  AdminGroupsInstanceTypes, AdminGroupsVolumes):

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
          quotaCpu
          quotaGpu
          quotaMemory
          projectQuotaCpu
          projectQuotaGpu
          projectQuotaMemory
          sharedVolumeCapacity
        }
        """ + group_basic_info

        apply_auto_fill(config)

        # cannot specify admins when creating
        if config.get('admins'):
            config['admins'] = ''

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
        """ + group_basic_info

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
        group = results['data']['group']
        if not group:
            return group

        group['volumes'] = group.pop('datasets', '[]')
        self._output_format_admins(id, group)
        return group

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
        mutation UpdateGroup(
          $data: GroupUpdateInput!,
          $where: GroupWhereUniqueInput!
        ) {
          updateGroup(data: $data, where: $where) {
            ...GroupBasicInfo
          }
        }
        """ + group_basic_info

        if config.get('admins'):
            config['admins'] = self._transform_admins(id, config.get('admins', []))

        variables = {'where': {'id': id}, 'data': validate(config, True)}
        results = self.request(variables, query)

        if 'data' not in results:
            return results

        updated_query = """
        query Group(
          $where: GroupWhereUniqueInput!
        ) {
          group(where: $where) {
            ...GroupBasicInfo
          }
        }
        """ + group_basic_info
        updated_results = self.request({'where': {'id': id}}, updated_query)
        if 'data' not in updated_results:
            return updated_results
        updated_group = updated_results['data']['group']
        self._output_format_admins(id, updated_group)
        return updated_group

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

    def _transform_admins(self, id: str, user_ids: List[str]):
        if len(user_ids) == 0:
            return ''

        member_dict = {}
        users = self.primehub.admin.admin_groups.list_users(id)
        for user in users:
            user_id = user['id']
            username = user['username']
            member_dict[user_id] = username

        admin_usernames = []
        invalid_user_ids = []
        for user_id in user_ids:
            if user_id in member_dict:
                admin_usernames.append(member_dict[user_id])
            else:
                invalid_user_ids.append(user_id)

        if len(invalid_user_ids) > 0:
            _invalid_ids = ', '.join(invalid_user_ids)
            msg = f'admins contain invalid user ids: {_invalid_ids}'
            raise PrimeHubException(msg)
        return ','.join(admin_usernames)

    def _output_format_admins(self, id: str, group: dict):
        admin_users = []
        admin_usernames = group.get('admins', '').split(',')
        users = self.primehub.admin.admin_groups.list_users(id)
        for user in users:
            if user['username'] in admin_usernames:
                admin_users.append(dict(
                    id=user['id'],
                    username=user['username']
                ))
        group['admins'] = admin_users

    def help_description(self):
        return "Manage groups"
