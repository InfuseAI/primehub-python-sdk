import json
import re
from typing import Iterator, Union, Any

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag, toggle_flag
from primehub.utils.validator import validate_groups

EMAIL_FORMAT_ERROR = 'Please fill a valid email address format.'

USERNAME_FORMAT_ERROR = r'''[username] Only lower case alphanumeric characters, '-', '.', '''
USERNAME_FORMAT_ERROR += r'''and underscores ("_") are allowed, and must start with a letter or numeric.'''


def invalid_config(message: str):
    example = """
    {"username":"user1","groups":{"connect":[{"id":"fc620866-91e6-4a7e-a576-7cdfbb5e2ea7"}]}}
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def validate_name(payload: dict):
    if 'username' not in payload:
        raise PrimeHubException('username is required')

    matched: Union[str, Any, None] = re.match(
        r'^[a-z0-9][-a-z0-9_.@]*$',
        payload.get('username'))

    # check formats
    if not matched:
        raise PrimeHubException(USERNAME_FORMAT_ERROR)


def validate_email(payload: dict):
    if 'email' not in payload:
        return

    matched: Union[str, Any, None] = re.match(
        r'(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))'
        r'@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
        payload.get('email'))

    # check formats
    if not matched:
        raise PrimeHubException(EMAIL_FORMAT_ERROR)


def validate(payload, for_update=False):
    if not for_update:
        validate_name(payload)
    else:
        if 'username' in payload:
            payload.pop('username')

    validate_email(payload)
    validate_groups(payload)

    volume_capacity = payload.get('volumeCapacity')
    if volume_capacity is not None:
        if not isinstance(volume_capacity, int):
            raise PrimeHubException('volumeCapacity must be an integer number')

    return payload


class AdminUsers(Helpful, Module):

    @cmd(name='list', description='List users', return_required=True, optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator:
        """
        List users

        :type page: int
        :param page: the page of all data

        :rtype Iterator
        :return user iterator
        """
        query = """
        query UsersConnection(
          $userAfter: String
          $userBefore: String
          $userLast: Int
          $userFirst: Int
          $where: UserWhereInput
          $userOrderBy: UsersOrderBy
        ) {
          users: usersConnection(
            after: $userAfter
            before: $userBefore
            last: $userLast
            first: $userFirst
            where: $where
            userOrderBy: $userOrderBy
          ) {
            edges {
              cursor
              node {
                id
                username
                email
                firstName
                lastName
                enabled
                isAdmin
              }
            }
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
          }
        }
        """

        # even the user connection does not support `page`, but it returns the cursor as the page `index`
        # we can convert the cursor to `page`
        variables = {'userAfter': '0', 'userFirst': 10}
        page = kwargs.get('page', 0)
        if page > 0:
            variables['userAfter'] = str(page - 1)
            results = self.request(variables, query)
            for e in results['data']['users']['edges']:
                yield e['node']
            return

        page = 1
        while True:
            variables['userAfter'] = str(page - 1)
            results = self.request(variables, query)
            if results['data']['users']['edges']:
                for e in results['data']['users']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    @cmd(name='create', description='Create a user', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Create a user

        :type file: str
        :param file: The file path of the configurations

        :rtype dict
        :return The user
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('The configuration is required.')
        return self.create(config)

    def create(self, config):
        """
        Create a user

        :type config: dict
        :param config: The configurations for creating a user

        :rtype dict
        :return The user
        """
        payload = validate(config)

        query = """
        mutation CreateUser($payload: UserCreateInput!) {
          createUser(data: $payload) {
            id
            username
          }
        }
        """

        results = self.request({'payload': validate(payload)}, query)
        if 'data' not in results:
            return results
        return results['data']['createUser']

    @cmd(name='update', description='Update the user', optionals=[('file', file_flag)])
    def _update_cmd(self, id: str, **kwargs):
        """
        Update the user

        :type id: str
        :param id: the id of the user

        :rtype: dict
        :returns: the user
        """
        return self.update(id, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, id: str, config: dict):
        """
        Update the user

        :type id: str
        :param id: the id of the user

        :rtype: dict
        :returns: the user
        """
        if not config:
            invalid_config('The configuration is required.')
        validate(config, True)

        query = """
        mutation UpdateUser($payload: UserUpdateInput!, $where: UserWhereUniqueInput!) {
          updateUser(data: $payload, where: $where) {
            id
            username
          }
        }
        """

        results = self.request({'where': {'id': id}, 'payload': config}, query)
        if 'data' not in results:
            return results

        return results['data']['updateUser']

    @cmd(name='get', description='Get an user by id', return_required=True)
    def get(self, id: str) -> dict:
        """
        Get an user by id

        :type id: str
        :param id: the id of an user

        :rtype dict
        :return the user
        """
        query = """
        query User($where: UserWhereUniqueInput!) {
          user(where: $where) {
            id
            username
            email
            firstName
            lastName
            enabled
            isAdmin
            volumeCapacity
            groups {
              id
              name
              displayName
              quotaCpu
              quotaGpu
            }
          }
        }
        """

        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results
        user = results['data']['user']

        # hide the everyone group
        groups = user['groups']
        user['groups'] = [x for x in groups if x['name'] != 'everyone']
        return user

    @cmd(name='delete', description='Delete an user by id', return_required=True)
    def delete(self, id: str) -> dict:
        """
        Delete an user by id

        :type id: str
        :param id: the id of the user

        :rtype dict
        :return the user
        """

        query = """
        mutation DeleteUser($where: UserWhereUniqueInput!) {
          deleteUser(where: $where) {
            id
            username
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results
        return results['data']['deleteUser']

    @cmd(name='reset-password', description='Reset password by id', return_required=True,
         optionals=[('temporary', toggle_flag)])
    def reset_password(self, id: str, password: str, **kwargs) -> dict:
        """
        Reset password by id

        :type id: str
        :param id: the id of the user

        :type id: str
        :param id: password

        :type temporary: bool
        :param temporary: make the password temporary

        :rtype dict
        :return the user
        """

        query = """
        mutation ResetPassword($id: String, $password: String, $temporary: Boolean) {
          resetPassword(id: $id, password: $password, temporary: $temporary) {
            id
          }
        }
        """

        temporary = kwargs.get('temporary', False)
        results = self.request({'id': id, 'password': password, 'temporary': temporary}, query)
        if 'data' not in results:
            return results
        return results['data']['resetPassword']

    def help_description(self):
        return "Manage users"
