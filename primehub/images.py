import json
from typing import Optional

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag
from primehub.resource_operations import GroupResourceOperation
from primehub.utils.validator import validate_name


class Images(Helpful, Module, GroupResourceOperation):
    """
    List images or get an image from the list
    """
    resource_name = 'images'
    query = """
    {
      me {
        effectiveGroups {
          name
          images {
            id
            name
            displayName
            description
            useImagePullSecret
            spec
          }
        }
      }
    }
    """

    @cmd(name='list', description='List images')
    def list(self) -> list:
        """
        List images

        :rtype: list
        :returns: all images in the current group
        """
        return self.do_list(Images.query, Images.resource_name)

    @cmd(name='get', description='Get an image by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get an image from the current group

        :type name: str
        :param name: the name of an image

        :rtype: Optional[dict]
        :returns: an image
        """
        return self.do_get(Images.query, Images.resource_name, name)

    @cmd(name='create', description='Create an image', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Create an image for the current group

        :type file: str
        :param file: The file path of the configurations

        :rtype dict
        :return The image
        """
        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('The configuration is required.')

        return self.create(config)

    def create(self, config):
        """
        Create an image for the current group

        :type config: dict
        :param config: The configurations for creating an image

        :rtype dict
        :return The image
        """
        payload = validate(config)
        payload['groups'] = {'connect': [{'id': self.group_id}]}
        payload['groupName'] = self.group_name

        query = """
        mutation CreateImageMutation($data: ImageCreateInput!) {
          createImage(data: $data) {
            id
          }
        }
        """

        results = self.request({'data': payload}, query)
        if 'data' not in results:
            return results
        return results['data']['createImage']

    @cmd(name='delete', description='Delete an image by name', return_required=True)
    def delete(self, name):
        """
        Delete an image by id

        :type id: str
        :param id: the id of an image

        :rtype dict
        :return an image
        """

        query = """
        mutation DeleteImageMutation($where: ImageWhereUniqueInput!) {
          deleteImage(where: $where) {
            id
          }
        }
        """
        self.get(name)

        results = self.request({'where': {'id': name}}, query)
        if 'data' not in results:
            return results
        return results['data']['deleteImage']

    def help_description(self):
        return "Get a image or list images"


def validate(payload: dict, for_update=False):
    if not for_update:
        validate_name(payload)

    image_type = payload.get('type')
    if image_type is not None and image_type not in ['cpu', 'gpu', 'both']:
        raise PrimeHubException("type should be one of ['cpu', 'gpu', 'both']")
    url = payload.get('url')
    if url is None:
        raise PrimeHubException("url is required")

    return payload


def invalid_config(message: str):
    example = """
    {
      "name": "base",
      "displayName": "Base image",
      "description": "base-notebook with python 3.7",
      "type": "both",
      "url": "infuseai/docker-stacks:base-notebook-63fdf50a",
      "urlForGpu": "infuseai/docker-stacks:base-notebook-63fdf50a-gpu"
    }
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))
