from typing import Optional

from primehub import Helpful, cmd, Module
from primehub.resource_operations import GroupResourceOperation


class Volumes(Helpful, Module, GroupResourceOperation):
    """
    List volumes or get a volume entry from the list
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

    @cmd(name='list', description='List volumes')
    def list(self) -> list:
        """
        List volumes

        :rtype: list
        :returns: all volumes in the current group
        """
        return self.do_list(Volumes.query, Volumes.resource_name)

    @cmd(name='get', description='Get a volume by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get a volume from the current group
        :type name: str
        :param name: the name of a volume
        :rtype: Optional[dict]
        :returns: a volume
        """
        return self.do_get(Volumes.query, Volumes.resource_name, name)

    def help_description(self):
        return "Get a volume or list volumes"
