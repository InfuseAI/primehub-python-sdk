import json
from typing import Iterator, Dict, Any

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException, resource_not_found
from primehub.utils.optionals import file_flag
from primehub.utils.validator import validate_name, validate_groups


def _error_handler(response):
    import re

    if 'errors' in response:
        message = [x for x in response['errors'] if 'message' in x]
        if message:
            message = message[0]['message']
            result = re.findall(r'images.primehub.io "([^"]+)" not found', message)
            if result:
                resource_not_found('images', result[0], 'id')


class AdminImages(Helpful, Module):

    @cmd(name='create', description='Create an image', optionals=[('file', file_flag), ('from', str)])
    def _create_cmd(self, **kwargs):
        """
        Create an image

        :type file: str
        :param file: The file path of the configurations

        :rtype dict
        :return The image
        """
        if kwargs.get('from', None):
            return self.submit_from_schedule(kwargs['from'])

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('The configuration is required.')

        return self.create(config)

    def create(self, config):
        """
        Create an image

        :type config: dict
        :param config: The configurations for creating an image

        :rtype dict
        :return The image
        """
        payload = validate(config)

        query = """
        """

        results = self.request({'payload': validate(payload)}, query)
        if 'data' not in results:
            return results
        return

    @cmd(name='update', description='Update the image', optionals=[('file', file_flag)])
    def _update_cmd(self, id: str, **kwargs):
        """
        Update the image

        :type id: str
        :param id: the id of the image

        :rtype: dict
        :returns: the image
        """
        return self.update(id, primehub_load_config(filename=kwargs.get('file', None)))

    def update(self, id: str, config: dict):
        self._valid_update(config, id)

        query = """
        """

        results = self.request({'where': {'id': id}, 'payload': config}, query, _error_handler)
        if 'data' not in results:
            return results

        return

    def _valid_update(self, config, id):
        existing_config = self.get(id)
        if existing_config is not None:
            validate(existing_config, True)

    @cmd(name='get', description='Get an image by id', return_required=True)
    def get(self, id: str) -> dict:
        """
        Get an image by id

        :type id: str
        :param id: the id of an image

        :rtype dict
        :return an image
        """
        query = """
        query ImageQuery($where: ImageWhereUniqueInput!) {
          image(where: $where) {
            id
            name
            displayName
            description
            type
            url
            urlForGpu
            useImagePullSecret
            global
            groups {
              id
              name
              displayName
            }
            isReady
            imageSpec {
              baseImage
              pullSecret
              packages {
                apt
                conda
                pip
              }
            }
            jobStatus {
              phase
            }
            logEndpoint
          }
        }
        """

        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results
        return results['data']['image']

    @cmd(name='delete', description='Delete an image by id', return_required=True)
    def delete(self, id):
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
        results = self.request({'where': {'id': id}}, query)
        if 'data' not in results:
            return results
        return results['data']['deleteImage']

    @cmd(name='list', description='List images', return_required=True, optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator:
        """
        List images

        :type page: int
        :param page: the page of all data

        :rtype Iterator
        :return image iterator
        """
        query = """
        query ImagesQuery($page: Int, $where: ImageWhereInput, $orderBy: ImageOrderByInput) {
          imagesConnection(
            page: $page
            orderBy: $orderBy
            where: $where
            mode: SYSTEM_ONLY
          ) {
            edges {
              cursor
              node {
                id
                name
                displayName
                description
                type
                isReady
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
            for e in results['data']['imagesConnection']['edges']:
                yield e['node']
            return

        page = 1
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['imagesConnection']['edges']:
                for e in results['data']['imagesConnection']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    def help_description(self):
        return "Manage images"


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

    return payload


def invalid_config(message: str):
    example = """
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))
