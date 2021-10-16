from typing import Any, Dict, Optional

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag


class AdminImages(Helpful, Module):

    @cmd(name='create', description='Create a image', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs) -> list:
        """
        Create a image

        :rtype: dict
        :returns: the image
        """

        return self.create(primehub_load_config(filename=kwargs.get('file', None)))

    def create(self, config) -> list:
        """
        Create a image

        :rtype: dict
        :returns: the image
        """

        query = """
        mutation CreateImageMutation($payload: ImageCreateInput!) {
          createImage(data: $payload) {
            name
            displayName
            description
            type
            url
            urlForGpu
            groupName
            global
            useImagePullSecret
          }
        }
        """

        variables = {'payload': validate_creation(validate(config))}
        result = self.request(variables, query)
        # if 'data' in result and 'createImage' in result['data']:
        #     return waring_if_needed(result['data']['createImage'], self.primehub.stderr)
        return result

    @cmd(name='update', description='Update the image')
    def _update_cmd(self, name: str, **kwargs) -> list:
        """
        Update the image

        :type name: str
        :rtype: dict
        :returns: the image
        """
        return self.update(name, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, name: str, config: dict) -> list:
        """
        Update the image

        :type name: str
        :type config: dict
        :rtype: dict

        :returns: the image
        """

        query = """
        mutation UpdateImageMutation($payload: ImageUpdateInput!, $where: ImageWhereUniqueInput!) {
          updateImage(data: $payload, where: $where) {
            name
            displayName
            description
            type
            url
            urlForGpu
            groupName
            global
            useImagePullSecret
          }
        }
        """

        update_mode = True
        variables = {'payload': validate(config, update_mode), 'where': {'id': name}}
        result = self.request(variables, query)
        # if 'data' in result and 'createImage' in result['data']:
        #     return waring_if_needed(result['data']['createImage'], self.primehub.stderr)
        return result

    @cmd(name='delete', description='Delete a image by id', return_required=True)
    def delete(self, id):
        """
        Delete a image by id

        :type id: str
        :param id: The image id

        :rtype dict
        :return the result of the deleted image
        """

        query = """
        mutation DeleteImageMutation($where: ImageWhereUniqueInput!) {
          deleteImage(where: $where) {
            id
          }
        }
        """

        result = self.request({'where': {'id': id}}, query)
        if 'data' in result and 'deleteImage' in result['data']:
            return result['data']['deleteImage']
        return result

    def help_description(self):
        return "Manage images"


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
