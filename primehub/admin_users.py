from typing import Any, Dict, Optional

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag


class AdminUsers(Helpful, Module):

    @cmd(name='create', description='Create a user', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs) -> list:
        """
        Create a user

        :rtype: dict
        :returns: the user
        """

        return self.create(primehub_load_config(filename=kwargs.get('file', None)))

    def create(self, config) -> list:
        """
        Create a user

        :rtype: dict
        :returns: the user
        """

        query = """
        mutation CreateUserMutation($payload: UserCreateInput!) {
          createUser(data: $payload) {
            username
            email
          }
        }
        """

        variables = {'payload': validate_creation(validate(config))}
        result = self.request(variables, query)
        # if 'data' in result and 'createUser' in result['data']:
        #     return waring_if_needed(result['data']['createUser'], self.primehub.stderr)
        return result

    @cmd(name='update', description='Update the user')
    def _update_cmd(self, name: str, **kwargs) -> list:
        """
        Update the user

        :type name: str
        :rtype: dict
        :returns: the user
        """
        return self.update(name, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, name: str, config: dict) -> list:
        """
        Update the user

        :type name: str
        :type config: dict
        :rtype: dict

        :returns: the user
        """

        query = """
        mutation UpdateUserMutation($payload: UserUpdateInput!, $where: UserWhereUniqueInput!) {
          updateUser(data: $payload, where: $where) {
              email
          }
        }
        """

        update_mode = True
        variables = {'payload': validate(config, update_mode), 'where': {'id': name}}
        result = self.request(variables, query)
        # if 'data' in result and 'createUser' in result['data']:
        #     return waring_if_needed(result['data']['createUser'], self.primehub.stderr)
        return result

    @cmd(name='delete', description='Delete a user by id', return_required=True)
    def delete(self, id):
        """
        Delete a user by id

        :type id: str
        :param id: The user id

        :rtype dict
        :return the result of the deleted user
        """

        query = """
        mutation DeleteUserMutation($where: UserWhereUniqueInput!) {
          deleteUser(where: $where) {
            id
          }
        }
        """

        result = self.request({'where': {'id': id}}, query)
        if 'data' in result and 'deleteUser' in result['data']:
            return result['data']['deleteUser']
        return result

    def help_description(self):
        return "Manage users"


def validate(payload: dict, for_update=False):
    # check required fields
    # if not for_update:
    #     if 'name' not in payload:
    #         raise PrimeHubException('name is required')
    #     if 'type' not in payload:
    #         raise PrimeHubException('type is required')

    #     matched: Union[str, Any, None] = re.match(
    #         r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*',
    #         payload.get('name'))

    #     # check formats
    #     if not matched:
    #         raise PrimeHubException("[name] should be lower case alphanumeric characters, '-' or '.', "
    #                                 "and must start and end with an alphanumeric character.")

    #     # check type values
    #     valid_types = ['pv', 'nfs', 'hostPath', 'git', 'env']
    #     if payload.get('type') not in valid_types and not for_update:
    #         raise PrimeHubException(f'[type] should be one of {valid_types}')

    #     # writable means could connect to groups for writable and enabling upload server
    #     writable_types = ['pv', 'nfs', 'hostPath']
    #     if 'enableUploadServer' in payload and payload.get('type') not in writable_types:
    #         raise PrimeHubException(f'[enableUploadServer] only can use with should be one of {writable_types} types')

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
    # url_types = ['both', 'cpu', 'gpu']
    # if 'pv' == payload.get('type'):
    #     provision = payload.get('pvProvisioning', '')
    #     if provision not in provision_types:
    #         raise PrimeHubException(
    #             f'pvProvisioning is required for pv type and its value should be one of {provision_types}')

    return payload
