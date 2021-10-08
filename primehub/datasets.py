import json
import re
from typing import Optional, Union, Any, Dict

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.resource_operations import GroupResourceOperation
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag


def invalid_config(message: str):
    example = """
    {"name":"my-dataset-name","displayName":"the dataset created by SDK",
    "description":"desc","type":"pv","global":false,"groups":
    {"connect":[{"id":"a7a283b5-c0e2-4b79-a78c-39c630324762","writable":true}]},"pvProvisioning":"auto","volumeSize":1}
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def validate(payload: dict, for_update=False):
    # check required fields
    if not for_update:
        if 'name' not in payload:
            raise PrimeHubException('name is required')
        if 'type' not in payload:
            raise PrimeHubException('type is required')

        matched: Union[str, Any, None] = re.match(
            r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*',
            payload.get('name'))

        # check formats
        if not matched:
            raise PrimeHubException("[name] should be lower case alphanumeric characters, '-' or '.', "
                                    "and must start and end with an alphanumeric character.")

        # check type values
        valid_types = ['pv', 'nfs', 'hostPath', 'git', 'env']
        if payload.get('type') not in valid_types and not for_update:
            raise PrimeHubException(f'[type] should be one of {valid_types}')

        # writable means could connect to groups for writable and enabling upload server
        writable_types = ['pv', 'nfs', 'hostPath']
        if 'enableUploadServer' in payload and payload.get('type') not in writable_types:
            raise PrimeHubException(f'[enableUploadServer] only can use with should be one of {writable_types} types')

    # check groups format
    if 'groups' in payload:
        groups: Optional[Dict[Any, Any]] = payload.get('groups')
        if groups:
            for g in groups.get('connect', []):
                if not isinstance(g, dict):
                    raise PrimeHubException('group connect should be a pair {id, writable}')
                if 'id' in g and 'writable' in g:
                    continue
                raise PrimeHubException('group connect should be a pair {id, writable}')

            for g in groups.get('disconnect', []):
                if not isinstance(g, dict):
                    raise PrimeHubException('disconnect connect should be an entry {id}')
                if 'id' in g and len(g) == 1:
                    continue
                raise PrimeHubException('disconnect connect should be an entry {id}')

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


def waring_if_needed(data: dict, stderr):
    if data and 'uploadServerSecret' in data:
        if data.get('uploadServerSecret') is None:
            print('WARNING: you got a nil uploadServerSecret, '
                  'because there is another one has been generated.\n',
                  file=stderr)
    return data


class Datasets(Helpful, Module, GroupResourceOperation):
    """
    List datasets or get a dataset entry from the list
    """
    resource_name = 'datasets'
    query = """
    query {
      me {
        effectiveGroups {
          name
          datasets {
            id
            name
            displayName
            description
            type
          }
        }
      }
    }
    """

    @cmd(name='create', description='Create a dataset', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs) -> list:
        """
        Create a dataset

        :rtype: dict
        :returns: the dataset
        """

        return self.create(primehub_load_config(filename=kwargs.get('file', None)))

    def create(self, config) -> list:
        """
        Create a dataset

        :rtype: dict
        :returns: the dataset
        """

        query = """
        mutation CreateDatasetMutation($payload: DatasetCreateInput!) {
          createDataset(data: $payload) {
            id
          }
        }
        """

        if not config:
            invalid_config('Dataset configuration file is required.')

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

    @cmd(name='update', description='Update the dataset')
    def _update_cmd(self, name: str, **kwargs) -> list:
        """
        Update the dataset

        :type name: str
        :rtype: dict
        :returns: the dataset
        """
        return self._update_cmd(name, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, name: str, config: dict) -> list:
        """
        Update the dataset

        :type name: str
        :type config: dict
        :rtype: dict

        :returns: the dataset
        """

        query = """
        mutation UpdateDatasetMutation($payload: DatasetUpdateInput!, $where: DatasetWhereUniqueInput!) {
          updateDataset(data: $payload, where: $where) {
            id
          }
        }
        """

        if not config:
            invalid_config('Dataset configuration file is required.')

        if config.get('enableUploadServer', False):
            query = """
            mutation UpdateDatasetMutation($payload: DatasetUpdateInput!, $where: DatasetWhereUniqueInput!) {
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

    @cmd(name='list', description='List datasets')
    def list(self) -> list:
        """
        List datasets

        :rtype: list
        :returns: all datasets in the current group
        """
        return self.do_list(Datasets.query, Datasets.resource_name)

    @cmd(name='get', description='Get a dataset by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get a dataset from the current group

        :type name: str
        :param name: the name of a dataset

        :rtype: Optional[dict]
        :returns: a dataset
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

        def output(dataset: dict):
            dataset_output = dict()
            keep_fields = ['id', 'name', 'displayName', 'description', 'global', 'type', 'groups']

            if dataset.get('type') == 'env':
                keep_fields.append('variables')

            if dataset.get('type') == 'git':
                keep_fields.append('url')
                keep_fields.append('secret')

            if dataset.get('type') == 'pv':
                keep_fields.append('pvProvisioning')
                keep_fields.append('volumeSize')

            if dataset.get('type') == 'nfs':
                keep_fields.append('nfsServer')
                keep_fields.append('nfsPath')

            if dataset.get('type') == 'hostPath':
                keep_fields.append('hostPath')

            if dataset.get('type') in ['pv', 'nfs', 'hostPath']:
                keep_fields.append('enableUploadServer')
                keep_fields.append('uploadServerLink')

            for k, v in dataset.items():
                if k in keep_fields:
                    dataset_output[k] = v

            return dataset_output

        result = self.request({'where': {'id': name}}, query)
        if 'data' in result and 'dataset' in result['data']:
            return output(result['data']['dataset'])

        return result

    @cmd(name='delete', description='Delete a dataset by id', return_required=True)
    def delete(self, id):
        """
        Delete a dataset by id

        :type id: str
        :param id: The dataset id

        :rtype dict
        :return the result of the deleted dataset
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

    @cmd(name='upload_secret', description='Regenerate the secret of the upload server',
         return_required=True)
    def regenerate_upload_server_secret(self, id):
        """
        Regenerate the secret of the upload server

        :type id: str
        :param id: The dataset id or name

        :rtype dict
        :return the result of the deleted dataset
        """

        query = """
        mutation RegenerateUploadServerSecretMutation($where: DatasetWhereUniqueInput!) {
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

    def help_description(self):
        return "Get a dataset or list datasets"
