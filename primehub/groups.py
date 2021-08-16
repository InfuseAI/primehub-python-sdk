from typing import Optional

from primehub import Helpful, cmd, Module
from primehub.utils import resource_not_found


class Groups(Helpful, Module):
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
            }
          }
        }
        """
        results = self.request({}, query)
        return results['data']['me']['effectiveGroups']

    @cmd(name='get', description='Get group by name', return_required=True)
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

        resource_not_found('group', group_name, 'name')
        return None

    def help_description(self):
        return "Get a group or list groups"
