from typing import Optional

from primehub import Helpful, cmd, Module
from primehub.resource_operations import GroupResourceOperation


class InstanceTypes(Helpful, Module, GroupResourceOperation):
    """
    List instance types or get an instance type from the list
    """
    resource_name = 'instanceTypes'
    query = """
    query {
      me {
        effectiveGroups {
          name
          instanceTypes {
            id
            name
            displayName
            description
          }
        }
      }
    }
    """

    @cmd(name='list', description='List instance types')
    def list(self) -> list:
        """
        List instance types

        :rtype: list
        :returns: all instance types in the current group
        """
        return self.do_list(InstanceTypes.query, InstanceTypes.resource_name)

    @cmd(name='get', description='Get an instance type by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get an instance type from the current group

        :type name: str
        :param name: the name of an instance type

        :rtype: Optional[dict]
        :returns: an instance type
        """
        return self.do_get(InstanceTypes.query, InstanceTypes.resource_name, name)

    def help_description(self):
        return "Get an instance types of list instance types"
