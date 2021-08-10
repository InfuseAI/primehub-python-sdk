from typing import Optional

from primehub import Helpful, cmd, Module
from primehub.resource_operations import GroupResourceOperation


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

    @cmd(name='get', description='Get a image by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get an image from the current group

        :type name: str
        :param name: the name of an image

        :rtype: Optional[dict]
        :returns: an image
        """
        return self.do_get(Images.query, Images.resource_name, name)

    def help_description(self):
        return "Get a image or list images"
