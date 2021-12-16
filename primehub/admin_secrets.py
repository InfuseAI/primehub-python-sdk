import json
from typing import Iterator

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag
from primehub.utils.permission import ask_for_permission
from primehub.utils.validator import ValidationSpec


def invalid_config(message: str):
    example = """
    {"name":"secret-1","type":"opaque","secret":"secret content"}
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


class AdminSecrets(Helpful, Module):

    @cmd(name='list', description='List secrets', return_required=False, optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator:
        """
        List secrets

        :type page: int
        :param page: the page of all data

        :rtype Iterator
        :return secret iterator
        """
        query = """
        query GetSecrets($page: Int) {
          secretsConnection(page: $page) {
            edges {
              cursor
              node {
                id
                ...SecretParts
              }
            }
          }
        }
        fragment SecretParts on Secret {
          id
          name
          displayName
          type
          registryHost
          username
        }
        """

        variables = {}
        if kwargs.get('page', 0) > 0:
            variables['page'] = kwargs.get('page')

        results = self.request(variables, query)
        if 'secretsConnection' in results['data']:
            results = results['data']['secretsConnection']['edges']

        for e in results:
            yield e['node']

    @cmd(name='create', description='Create a secret', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Create a secret

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
        Create a secret

        :type config: dict
        :param config: The configurations for creating a secret

        :rtype dict
        :return The id of a secret
        """

        ValidationSpec("""
        input SecretCreateInput {
          name: ResourceID!
          type: SecretType!
          displayName: String
          secret: String
          registryHost: String
          username: String
          password: String
        }
        """).validate(config)

        query = """
        mutation CreateSecretMutation($payload: SecretCreateInput!) {
          createSecret(data: $payload) {
            id
          }
        }
        """

        results = self.request({'payload': config}, query)
        if 'data' not in results:
            return results
        return results['data']['createSecret']

    @cmd(name='update', description='Update the secret', optionals=[('file', file_flag)])
    def _update_cmd(self, id: str, **kwargs):
        """
        Update the secret

        :type id: str
        :param id: the id of the secret

        :rtype: dict
        :returns: the secret
        """
        return self.update(id, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, id: str, config: dict):
        """
        Update the secret

        :type id: str
        :param id: the id of the secret

        :rtype: dict
        :returns: the secret
        """
        if not config:
            invalid_config('The configuration is required.')

        query = """
        mutation UpdateSecretMutation(
          $payload: SecretUpdateInput!
          $where: SecretWhereUniqueInput!
        ) {
          updateSecret(data: $payload, where: $where) {
            id
          }
        }
        """

        ValidationSpec("""
        input SecretUpdateInput {
          displayName: String
          type: SecretType
          secret: String
          registryHost: String
          username: String
          password: String
        }
        """).validate(config)

        if config.get('type') and config.get('type') != self.get(id).get('type'):
            raise PrimeHubException('[type] can not be changed')

        results = self.request({'where': {'id': id}, 'payload': config}, query)
        if 'data' not in results:
            return results

        return results['data']['updateSecret']

    @cmd(name='get', description='Get an secret by id', return_required=True)
    def get(self, id: str) -> dict:
        """
        Get an secret by id

        :type id: str
        :param id: the id of a secret

        :rtype dict
        :return the secret
        """
        query = """
        query SecretQuery($where: SecretWhereUniqueInput!) {
          secret(where: $where) {
            id
            ...SecretParts
          }
        }
        fragment SecretParts on Secret {
          id
          name
          displayName
          type
          registryHost
          username
          password
        }
        """

        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results

        result = results['data']['secret']

        if result.get('type') == 'opaque':
            del result['registryHost']
            del result['username']
            del result['password']
        return result

    @ask_for_permission
    @cmd(name='delete', description='Delete a secret by id', return_required=True)
    def delete(self, id: str, **kwargs) -> dict:
        """
        Delete a secret by id

        :type id: str
        :param id: the id of the secret

        :rtype dict
        :return the secret
        """

        query = """
        mutation DeleteSecretMutation($where: SecretWhereUniqueInput!) {
          deleteSecret(where: $where) {
            id
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results
        return results['data']['deleteSecret']

    def help_description(self):
        return "Manage secrets"
