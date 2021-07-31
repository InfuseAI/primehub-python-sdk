from typing import Optional

from primehub import Helpful, cmd, Module


class Group(Helpful, Module):
    """
    List effective groups or get a group entry from the list
    """

    @cmd(name='list', description='List groups')
    def list(self) -> list:
        """
        List available groups

        :rtype: list
        :returns: all effective groups for your account
        """
        query = """
        {
          me {
            effectiveGroups {
              id
              name
              displayName
              # user quota
              quotaCpu
              quotaGpu
              quotaMemory
              # group quota
              projectQuotaCpu
              projectQuotaGpu
              projectQuotaMemory
              images {
                id
                name
                displayName
                description
                type
                url
                urlForGpu
                groupName
              }
              instanceTypes {
                id
                name
                displayName
                description
              }
              datasets {
                id
                name
                displayName
                description
              }
            }
          }
        }
        """
        results = self.request({}, query)
        return results['data']['me']['effectiveGroups']

    @cmd(name='get', description='Get group by name')
    def get(self, group_name: str) -> Optional[dict]:
        """
        Get a group from available groups

        :type group_name: str
        :param group_name: the name of a group

        :rtype: Optional[dict]
        :returns: a group entry from available groups
        """
        groups = self.list()
        group = [x for x in groups if x['name'] == group_name]
        if group:
            return group[0]
        return None

    def help_description(self):
        return "Get a group or list groups"
