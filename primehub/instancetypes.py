from typing import Optional

from primehub import Helpful, cmd, Module


class InstanceTypes(Helpful, Module):
    """
    List instance types or get an instance type from the list
    """

    def _list_instance_types(self, query):
        results = self.request({}, query)
        for g in results['data']['me']['effectiveGroups']:
            if self.group_name == g['name']:
                return g['instanceTypes']
        return []

    @cmd(name='list', description='List instance types')
    def list(self) -> list:
        """
        List instance types

        :rtype: list
        :returns: all instance types in the current group
        """

        query = """
        query {
          me {
            effectiveGroups {
              name
              instanceTypes {
                name
                displayName
                description
                cpuRequest
                cpuLimit
                memoryRequest
                memoryLimit
                gpuLimit
                global
              }
            }
          }
        }
        """

        return self._list_instance_types(query)

    @cmd(name='get', description='Get an instance type by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get an instance type from the current group

        :type name: str
        :param name: the name of an instance type

        :rtype: Optional[dict]
        :returns: an instance type
        """
        query = """
        query {
          me {
            effectiveGroups {
              name
              instanceTypes {
                name
                displayName
                description
                cpuRequest
                cpuLimit
                memoryRequest
                memoryLimit
                gpuLimit
                global
                tolerations {
                  operator
                  key
                  value
                  effect
                }
                nodeSelector
              }
            }
          }
        }
        """
        results = self._list_instance_types(query)
        for x in results:
            if x['name'] == name:
                return x

        return None

    def help_description(self):
        return "Get an instance types of list instance types"
