import json
from typing import Iterator, Dict, Any

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException, resource_not_found
from primehub.utils.optionals import file_flag
from primehub.utils.validator import validate_name, validate_groups

NODE_SELECTOR_KEY_LEN_ERROR = 'nodeSelector: len(key) should be less or equal to 63'
NODE_SELECTOR_KV_TYPE_ERROR = 'nodeSelector: key and value must be a string'

TOLERATION_EFFECT_ERROR = 'toleration: effect should be one of the ' \
                          '{NoSchedule, PreferNoSchedule and NoExecute}'

TOLERATION_EXISTS_OPERATOR_ERROR = 'toleration: should not set value for Exists operator'
TOLERATION_EQUAL_OPERATOR_ERROR = 'toleration: should set value for Equal operator'
TOLERATION_FORMAT_ERROR = 'tolerations should have the only one field "set"'
TOLERATION_OPERATOR_ERROR = 'toleration: operator should be one of Exists or Equal'

NODE_SELECTOR_FORMAT_ERROR = 'nodeSelector: content should be key-value pairs in json format'


def _error_handler(response):
    import re

    if 'errors' in response:
        message = [x for x in response['errors'] if 'message' in x]
        if message:
            message = message[0]['message']
            result = re.findall(r'instancetypes.primehub.io "([^"]+)" not found', message)
            if result:
                resource_not_found('instancetypes', result[0], 'id')


class AdminInstanceTypes(Helpful, Module):

    @cmd(name='create', description='Create an instance type', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Create an instance type

        :type file: str
        :param file: The file path of the configurations

        :rtype dict
        :return The instance type
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('The configuration is required.')

        return self.create(config)

    def create(self, config):
        """
        Create an instance type

        :type config: dict
        :param config: The configurations for creating an instance type

        :rtype dict
        :return The instance type
        """
        apply_auto_fill(config)
        payload = validate(config)

        query = """
        mutation CreateInstanceTypeMutation($payload: InstanceTypeCreateInput!) {
          createInstanceType(data: $payload) {
            id
          }
        }
        """

        results = self.request({'payload': validate(payload)}, query)
        if 'data' not in results:
            return results
        return results['data']['createInstanceType']

    @cmd(name='update', description='Update the instance type', optionals=[('file', file_flag)])
    def _update_cmd(self, id: str, **kwargs):
        """
        Update the instance type

        :type id: str
        :param id: the id of the instance type

        :rtype: dict
        :returns: the instance type
        """
        return self.update(id, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, id: str, config: dict):
        self._valid_update(config, id)

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

        results = self.request({'where': {'id': id}, 'payload': config}, query, _error_handler)
        if 'data' not in results:
            return results

        return results['data']['updateInstanceType']

    def _valid_update(self, config, id):
        existing_config = self.get(id)
        if existing_config is not None:

            # convert tolerations to create-form
            tolerations_list = existing_config.pop('tolerations')
            tolerations_set = {'set': tolerations_list}
            existing_config['tolerations'] = tolerations_set

            # remove unused fields
            removing_keys = ['name']
            for k in existing_config.keys():
                if existing_config[k] is None:
                    removing_keys.append(k)
            for k in set(removing_keys):
                if k in existing_config:
                    existing_config.pop(k)

            # merge input-config
            for k, v in config.items():
                existing_config[k] = v

            validate(existing_config, True)

    @cmd(name='get', description='Get an instance type by id', return_required=True)
    def get(self, id: str) -> dict:
        """
        Get an instance type by id

        :type id: str
        :param id: the id of an instance type

        :rtype dict
        :return an instance type
        """
        query = """
        query InstanceTypeInfoQuery($where: InstanceTypeWhereUniqueInput!) {
          instanceType(where: $where) {
            id
            cpuRequest
            memoryRequest
            global
            groups {
              id
              name
              displayName
              quotaCpu
              quotaGpu
            }
            tolerations {
              key
              value
              operator
              effect
            }
            nodeSelector
            ...InstanceTypeInfo
          }
        }

        fragment InstanceTypeInfo on InstanceType {
          id
          name
          displayName
          description
          cpuLimit
          memoryLimit
          gpuLimit
        }
        """
        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results

        results = results['data']['instanceType']
        return results

    @cmd(name='delete', description='Delete an instance type by id', return_required=True)
    def delete(self, id):
        """
        Delete an instance type by id

        :type id: str
        :param id: the id of an instance type

        :rtype dict
        :return an instance type
        """

        query = """
        mutation DeleteInstanceTypeMutation($where: InstanceTypeWhereUniqueInput!) {
          deleteInstanceType(where: $where) {
            id
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results

        return results['data']['deleteInstanceType']

    @cmd(name='list', description='List instance type', return_required=True, optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator:
        """
        List instance type

        :type page: int
        :param page: the page of all data

        :rtype Iterator
        :return instance type iterator
        """
        query = """
        query InstanceTypesQuery(
          $page: Int
          $where: InstanceTypeWhereInput
          $orderBy: InstanceTypeOrderByInput
        ) {
          instanceTypesConnection(page: $page, where: $where, orderBy: $orderBy) {
            edges {
              cursor
              node {
                id
                ...InstanceTypeInfo
              }
            }
            pageInfo {
              currentPage
              totalPage
            }
          }
        }
        fragment InstanceTypeInfo on InstanceType {
          id
          name
          displayName
          description
          cpuLimit
          memoryLimit
          gpuLimit
        }
        """
        variables = {'page': 1}
        page = kwargs.get('page', 0)
        if page:
            variables['page'] = page
            results = self.request(variables, query)
            for e in results['data']['instanceTypesConnection']['edges']:
                yield e['node']
            return

        page = 1
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['instanceTypesConnection']['edges']:
                for e in results['data']['instanceTypesConnection']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    def help_description(self):
        return "Manage instance type"


def apply_auto_fill(config: dict):
    if 'cpuLimit' not in config:
        config['cpuLimit'] = 1
    if 'memoryLimit' not in config:
        config['memoryLimit'] = 1


def required_field(field):
    return f'{field} is required'


def required_numeric_field(field):
    return f'{field} must be an integer or a float type'


def required_gt_0(field):
    return f'{field} must be greater than zero'


def required_int_field(field):
    return f'{field} must be an integer type'


def required_str_lengths_3_63(field):
    return f'{field} value must a string and len(value) between 3 and 63'


def validate(payload: dict, for_update=False):
    if not for_update:
        validate_name(payload)
    validate_groups(payload)

    validate_cpu_fields(payload)
    validate_memory_fields(payload)
    validate_gpu_field(payload)
    validate_tolerations_field(payload)
    validate_node_selector_field(payload)

    return payload


def validate_node_selector_field(payload: dict):
    node_selector = payload.get('nodeSelector', None)
    if node_selector is None:
        return
    if not isinstance(node_selector, dict):
        raise PrimeHubException(NODE_SELECTOR_FORMAT_ERROR)

    for k, v in node_selector.items():
        if not isinstance(k, str):
            raise PrimeHubException(NODE_SELECTOR_KV_TYPE_ERROR)
        if not isinstance(v, str):
            raise PrimeHubException(NODE_SELECTOR_KV_TYPE_ERROR)

        if len(k) > 63:
            raise PrimeHubException(NODE_SELECTOR_KEY_LEN_ERROR)


def validate_tolerations_field(payload: dict):
    tolerations: Dict[Any, Any] = payload.get('tolerations', {})
    if tolerations:
        if set(tolerations.keys()) != {'set'}:
            raise PrimeHubException(TOLERATION_FORMAT_ERROR)

    for idx, toleration in enumerate(tolerations.get('set', [])):
        k = toleration.get('key', None)
        v = toleration.get('value', None)

        operator = None
        if 'operator' in toleration:
            op = toleration.get('operator')
            if op is None:
                raise PrimeHubException(TOLERATION_OPERATOR_ERROR)

            if not isinstance(op, str):
                raise PrimeHubException(TOLERATION_OPERATOR_ERROR)

            if op != 'Equal' and op != 'Exists':
                raise PrimeHubException(TOLERATION_OPERATOR_ERROR)
            operator = op
        else:
            # by default, the operator is Equal
            operator = 'Equal'

        if operator == 'Equal' and v is None:
            raise PrimeHubException(TOLERATION_EQUAL_OPERATOR_ERROR)

        if operator == 'Exists' and v is not None:
            raise PrimeHubException(TOLERATION_EXISTS_OPERATOR_ERROR)

        if not isinstance(k, str) or (len(k) < 3 or len(k) > 63):
            raise PrimeHubException(required_str_lengths_3_63('key'))

        if not isinstance(v, str) or (len(v) < 3 or len(v) > 63):
            if operator != 'Exists':
                raise PrimeHubException(required_str_lengths_3_63('value'))

        if 'effect' in toleration and toleration.get('effect') \
                not in {'NoSchedule', 'PreferNoSchedule', 'NoExecute'}:
            raise PrimeHubException(TOLERATION_EFFECT_ERROR)


def validate_memory_fields(payload: dict):
    validate_limit_request_fields(payload, 'memoryLimit', 'memoryRequest')


def validate_cpu_fields(payload: dict):
    validate_limit_request_fields(payload, 'cpuLimit', 'cpuRequest')


def validate_gpu_field(payload: dict):
    gpu_limit = payload.get('gpuLimit', None)
    if gpu_limit is None:
        # gpu limit could be unset
        return

    if not isinstance(gpu_limit, int):
        raise PrimeHubException(required_int_field('gpuLimit'))

    if gpu_limit < 0:
        raise PrimeHubException(required_gt_0('gpuLimit'))


def validate_limit_request_fields(payload: dict, limit_field: str, request_field):
    resource_limit = payload.get(f'{limit_field}', None)
    if resource_limit is None:
        raise PrimeHubException(required_field(f'{limit_field}'))
    if isinstance(resource_limit, float) or isinstance(resource_limit, int):
        if resource_limit <= 0:
            raise PrimeHubException(required_gt_0(f'{limit_field}'))
    else:
        raise PrimeHubException(required_numeric_field(f'{limit_field}'))

    resource_request = payload.get(f'{request_field}', None)
    if resource_request is not None:
        if isinstance(resource_request, float) or isinstance(resource_request, int):
            if resource_request < 0:
                raise PrimeHubException(required_gt_0(f'{request_field}'))
            if resource_request > resource_limit:
                raise PrimeHubException(f'{request_field} should less or equal to {limit_field}')
        else:
            raise PrimeHubException(required_numeric_field(f'{request_field}'))


def invalid_config(message: str):
    example = """
    {"name":"cpu-1","displayName":"CPU 1","description":"1 vCPU / 1G Memory","cpuLimit":1,"memoryLimit":1,"gpuLimit":0,
    "global":true,"tolerations":
    {"set":[{"operator":"Equal","effect":"NoSchedule","key":"nvidia.com/gpu","value":"v100"}]}}
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))
