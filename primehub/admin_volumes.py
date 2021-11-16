import json
from typing import Optional

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag
from primehub.utils.validator import validate_name, validate_pv_groups


def waring_if_needed(data: dict, stderr):
    if data and 'uploadServerSecret' in data:
        if data.get('uploadServerSecret') is None:
            print('WARNING: you got a nil uploadServerSecret, '
                  'because there is another one has been generated.\n',
                  file=stderr)
    return data


class AdminVolumes(Helpful, Module):

    @cmd(name='create', description='Create a volume', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs) -> list:
        """
        Create a volume

        :rtype: dict
        :returns: the volume
        """

        return self.create(primehub_load_config(filename=kwargs.get('file', None)))

    def create(self, config) -> list:
        """
        Create a volume

        :rtype: dict
        :returns: the volume
        """

        query = """
        mutation CreateDatasetMutation($payload: DatasetCreateInput!) {
          createDataset(data: $payload) {
            id
          }
        }
        """

        if not config:
            invalid_config('Volume configuration file is required.')

        if config.get('enableUploadServer', False):
            query = """
            mutation CreateDatasetMutation($payload: DatasetCreateInput!) {
              createDataset(data: $payload) {
                id
                uploadServerSecret {
                  username
                  password
                }
              }
            }
            """

        variables = {'payload': validate_creation(validate(config))}
        result = self.request(variables, query)
        if 'data' in result and 'createDataset' in result['data']:
            return waring_if_needed(result['data']['createDataset'], self.primehub.stderr)
        return result

    @cmd(name='update', description='Update the volume')
    def _update_cmd(self, name: str, **kwargs) -> list:
        """
        Update the volume

        :type name: str
        :rtype: dict
        :returns: the volume
        """
        return self.update(name, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, name: str, config: dict) -> list:
        """
        Update the volume

        :type name: str
        :type config: dict
        :rtype: dict

        :returns: the volume
        """

        query = """
        mutation UpdateDatasetMutation(
          $payload: DatasetUpdateInput!
          $where: DatasetWhereUniqueInput!
        ) {
          updateDataset(data: $payload, where: $where) {
            id
          }
        }
        """

        if not config:
            invalid_config('Volume configuration file is required.')

        if config.get('enableUploadServer', False):
            query = """
            mutation UpdateDatasetMutation(
              $payload: DatasetUpdateInput!
              $where: DatasetWhereUniqueInput!
            ) {
              updateDataset(data: $payload, where: $where) {
                id
                uploadServerSecret {
                  username
                  password
                }
              }
            }
            """

        update_mode = True
        variables = {'payload': validate(config, update_mode), 'where': {'id': name}}
        result = self.request(variables, query)
        if 'data' in result and 'updateDataset' in result['data']:
            return waring_if_needed(result['data']['updateDataset'], self.primehub.stderr)
        return result

    @cmd(name='regen-upload-secret', description='Regenerate the secret of the upload server',
         return_required=True)
    def regenerate_upload_server_secret(self, id):
        """
        Regenerate the secret of the upload server

        :type id: str
        :param id: The volume id or name

        :rtype dict
        :return the result of the deleted volume
        """

        query = """
        mutation RegenerateUploadServerSecretMutation(
          $where: DatasetWhereUniqueInput!
        ) {
          regenerateUploadServerSecret(where: $where) {
            id
            uploadServerSecret {
              username
              password
            }
          }
        }
        """

        result = self.request({'where': {'id': id}}, query)
        if 'data' in result and 'regenerateUploadServerSecret' in result['data']:
            return waring_if_needed(result['data']['regenerateUploadServerSecret'], self.primehub.stderr)
        return result

    @cmd(name='list', description='List volumes', return_required=True, optionals=[('page', int)])
    def list(self, **kwargs):
        query = """
        query GetDatasets(
          $page: Int
          $orderBy: DatasetOrderByInput
          $where: DatasetWhereInput
        ) {
          datasetsConnection(page: $page, orderBy: $orderBy, where: $where) {
            edges {
              cursor
              node {
                id
                name
                displayName
                description
                type
                uploadServerLink
              }
            }
            pageInfo {
              currentPage
              totalPage
            }
          }
        }
        """
        variables = {'page': 1}
        page = kwargs.get('page', 0)
        if page:
            variables['page'] = page
            results = self.request(variables, query)
            for e in results['data']['datasetsConnection']['edges']:
                yield e['node']
            return

        page = 1
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['datasetsConnection']['edges']:
                for e in results['data']['datasetsConnection']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    @cmd(name='delete', description='Delete a volume by id', return_required=True)
    def delete(self, id):
        """
        Delete a volume by id

        :type id: str
        :param id: The volume id

        :rtype dict
        :return the result of the deleted volume
        """

        query = """
        mutation DeleteDatasetMutation($where: DatasetWhereUniqueInput!) {
          deleteDataset(where: $where) {
            id
          }
        }
        """

        result = self.request({'where': {'id': id}}, query)
        if 'data' in result and 'deleteDataset' in result['data']:
            return result['data']['deleteDataset']
        return result

    @cmd(name='get', description='Get a volume by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get a volume from the current group

        :type name: str
        :param name: the name of a volume

        :rtype: Optional[dict]
        :returns: a volume
        """

        query = """
        query DatasetQuery($where: DatasetWhereUniqueInput!) {
          dataset(where: $where) {
            id
            name
            displayName
            description
            type
            pvProvisioning
            volumeSize
            variables
            nfsServer
            nfsPath
            hostPath
            url
            secret {
              id
            }
            enableUploadServer
            uploadServerLink
            global
            groups {
              id
              name
              displayName
              writable
            }
          }
        }
        """

        result = self.request({'where': {'id': name}}, query)
        if 'data' in result and 'dataset' in result['data']:
            return volume_output(result['data']['dataset'])

        return result

    def help_description(self):
        return "Manage volumes"


def invalid_config(message: str):
    example = """
    {"name":"my-volume-name","displayName":"the volume created by SDK",
    "description":"desc","type":"pv","global":false,"groups":
    {"connect":[{"id":"a7a283b5-c0e2-4b79-a78c-39c630324762","writable":true}]},"pvProvisioning":"auto","volumeSize":1}
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def validate(payload: dict, for_update=False):
    # check required fields
    if not for_update:
        validate_name(payload)
        if 'type' not in payload:
            raise PrimeHubException('type is required')

        # check type values
        valid_types = ['pv', 'nfs', 'hostPath', 'git', 'env']
        if payload.get('type') not in valid_types and not for_update:
            raise PrimeHubException(f'[type] should be one of {valid_types}')

        # writable means could connect to groups for writable and enabling upload server
        writable_types = ['pv', 'nfs', 'hostPath']
        if 'enableUploadServer' in payload and payload.get('type') not in writable_types:
            raise PrimeHubException(f'[enableUploadServer] only can use with should be one of {writable_types} types')

    # check groups format
    validate_pv_groups(payload)
    return payload


def validate_creation(payload: dict):
    # validate type specific fields
    provision_types = ['auto', 'manual']
    if 'pv' == payload.get('type'):
        provision = payload.get('pvProvisioning', '')
        if provision not in provision_types:
            raise PrimeHubException(
                f'pvProvisioning is required for pv type and its value should be one of {provision_types}')

    if 'nfs' == payload.get('type'):
        if not payload.get('nfsServer') or not payload.get('nfsPath'):
            raise PrimeHubException(
                'nfsServer and nfsPath are required for nfs type')

    if 'hostPath' == payload.get('type'):
        if 'hostPath' not in payload:
            raise PrimeHubException(
                'hostPath is required for hostPath type')

    if 'git' == payload.get('type'):
        if 'url' not in payload:
            raise PrimeHubException(
                'url is required for git type')
        if 'secret' in payload:
            secret_connect = payload.get('secret', {}).get('connect', {})
            if isinstance(secret_connect, dict):
                if 'id' not in secret_connect:
                    raise PrimeHubException('secret connect should have an entry')
            else:
                raise PrimeHubException('secret connect should have an entry')

    if 'secret' in payload and payload.get('type') != 'git':
        raise PrimeHubException(
            'secret only is used with git type')

    return payload


def volume_output(volume: dict):
    output = dict()
    keep_fields = ['id', 'name', 'displayName', 'description', 'global', 'type', 'groups']

    if volume.get('type') == 'env':
        keep_fields.append('variables')

    if volume.get('type') == 'git':
        keep_fields.append('url')
        keep_fields.append('secret')

    if volume.get('type') == 'pv':
        keep_fields.append('pvProvisioning')
        keep_fields.append('volumeSize')

    if volume.get('type') == 'nfs':
        keep_fields.append('nfsServer')
        keep_fields.append('nfsPath')

    if volume.get('type') == 'hostPath':
        keep_fields.append('hostPath')

    if volume.get('type') in ['pv', 'nfs', 'hostPath']:
        keep_fields.append('enableUploadServer')
        keep_fields.append('uploadServerLink')

    for k, v in volume.items():
        if k in keep_fields:
            output[k] = v

    return output
