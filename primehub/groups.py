from typing import Dict, Any, Optional

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

    @cmd(name='add-user', description='Add a user to a group by id')
    def add_user(self, group_id: str, user_id: str, is_admin: bool = False):
        """
        Add a user to a group by id. Only group admin can add users.

        :type group_id: str
        :param group_id: group id
        :type user_id: str
        :param user_id: user id
        :type is_admin: bool
        :param is_admin: 'True' if the user is added as group admin, and 'False' otherwise, \
defaults to False
        """
        groups = [x for x in self._list_with_admins() if x['id'] == group_id]
        if not groups:
            resource_not_found('group', group_id, 'id')
            return None
        admins = None
        if is_admin:
            admin_list = groups[0]['admins'].split(',')
            admin_list.append(self._get_username(user_id))
            admins = ','.join(admin_list)

        self._update_user(group_id, user_id, 'connect', admins)

    @cmd(name='remove-user', description='Remove a user from a group by id')
    def remove_user(self, group_id: str, user_id: str):
        """
        Remove a user from a group by id. Only group admin can remove users.

        :type group_id: str
        :param group_id: group id
        :type user_id: str
        :param user_id: user id
        """
        groups = [x for x in self._list_with_admins() if x['id'] == group_id]
        if not groups:
            resource_not_found('group', group_id, 'id')
            return None
        self._update_user(group_id, user_id, 'disconnect')

    def _list_with_admins(self):
        query = """
        {
          me {
            effectiveGroups {
              id
              admins
            }
          }
        }
        """
        results = self.request({}, query)
        return results['data']['me']['effectiveGroups']

    def _get_username(self, user_id: str):
        query = """
        query GetUsername($where: UserWhereUniqueInput!) {
          user (where: $where) {
            username
          }
        }
        """
        results = self.request({'where': {'id': user_id}}, query)
        return results['data']['user']['username']

    def _update_user(self, group_id: str, user_id: str, action: str, admins: Optional[str] = None):
        query = """
        mutation UpdateGroup($data: GroupUpdateInput!, $where: GroupWhereUniqueInput!) {
          updateGroup(data: $data, where: $where) {
            id
            name
            displayName
            admins
            users {
              id
              username
            }
          }
        }
        """
        data: Dict[str, Any] = {'users': {action: [{'id': user_id}]}}
        if admins:
            data['admins'] = admins
        results = self.request({'where': {'id': group_id}, 'data': data}, query)
        if 'data' not in results:
            return results
        return results['data']['updateGroup']

    def help_description(self):
        return "Get a group or list groups"
