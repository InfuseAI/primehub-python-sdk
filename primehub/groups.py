import json
from typing import Dict, Any, Optional

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.utils.optionals import file_flag, toggle_flag
from primehub.utils import resource_not_found, PrimeHubException

_mutation_mlflow = """
mutation UpdateGroupMLflowConfig($where: GroupWhereUniqueInput!, $data: GroupUpdateInput!) {
  updateGroup(where: $where, data: $data) {
    id
    name
    mlflow {
      trackingUri
      uiUrl
      trackingEnvs {
        name
        value
      }
      artifactEnvs {
        name
        value
      }
    }
  }
}
"""


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

    @cmd(name='list-users', description='List users in the group by id')
    def list_users(self, group_id: str):
        """
        List users in the group by id

        :type group_id: str
        :param group_id: group id
        :rtype: list
        :returns: users in the group
        """
        groups = [x for x in self._list_with_admins() if x['id'] == group_id]
        if not groups:
            resource_not_found('group', group_id, 'id')
            return None
        group_admins = groups[0]['admins'].split(',')
        users = groups[0]['users']
        for u in users:
            if u['username'] in group_admins:
                u['group_admin'] = True
            else:
                u['group_admin'] = False
        return users

    @cmd(name='add-user', description='Add a user to a group by id', optionals=[('is_admin', toggle_flag)])
    def _add_user(self, group_id: str, user_id: str, **kwargs):
        """
        Add a user to a group by id. Only group admin can add users.

        :type group_id: str
        :param group_id: group id
        :type user_id: str
        :param user_id: user id
        :type is_admin: bool
        :param is_admin: Add `--is_admin` if the user is added as group admin.
        """
        is_admin = kwargs.get('is_admin', False)
        self.add_user(group_id, user_id, is_admin)

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
              users {
                id
                username
                firstName
                lastName
                email
              }
            }
          }
        }
        """
        results = self.request({}, query)
        return results['data']['me']['effectiveGroups']

    def _get_username(self, user_id: str):
        query = """
        query GetUsername($where: UserWhereUniqueInput!) {
          user(where: $where) {
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

    @cmd(name='set-mlflow', description='Set MLflow config to a group by id', optionals=[('file', file_flag)])
    def _set_mlflow(self, group_id: str, **kwargs):
        """
        Set MLflow configuration to a group by id

        :type group_id: str
        :param group_id: group id
        :type file: str
        :param file: The file path of MLflow configuration
        """
        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            example = """
            {
              "tracking_uri":"http://app-mlflow-xyzab:5000",
              "ui_uri":"https://primehub-python-sdk.primehub.io/console/apps/mlflow-xyzab",
              "tracking_envs":[{"name":"key1","value":"value1"}],
              "artifact_envs":[{"name":"key1","value":"value1"}]
            }
            """.strip()
            field_help = "* 'tracking_uri' field is required"
            raise PrimeHubException('MLflow configuration is required.' +
                                    "\n\nExample:\n" +
                                    json.dumps(json.loads(example), indent=2) +
                                    f"\n\n{field_help}\n")
        return self.set_mlflow(group_id, config)

    def set_mlflow(self, group_id: str, config: dict):
        """
        Set MLflow configuration to a group by id

        :type group_id: str
        :param group_id: group id
        :type config: dict
        :param config: The content of MLflow configuration
        """
        query = _mutation_mlflow
        data = {
            "trackingUri": config.get('tracking_uri'),
            "uiUrl": config.get('ui_uri', ''),
            "trackingEnvs": config.get('tracking_envs', []),
            "artifactEnvs": config.get('artifact_envs', [])
        }
        if not data['trackingUri']:
            raise PrimeHubException("'tracking_uri' is required")

        results = self.request({'where': {'id': group_id}, 'data': data}, query)
        if 'data' not in results:
            return results

    @cmd(name='unset-mlflow', description='Unset MLflow config from a group by id')
    def unset_mlflow(self, group_id: str):
        """
        Unset MLflow configuration from a group by id

        :type group_id: str
        :param group_id: group id
        """
        query = _mutation_mlflow
        data: Dict[str, Any] = {
            "trackingUri": None,
            "uiUrl": None,
            "trackingEnvs": [],
            "artifactEnvs": [],
        }
        results = self.request({'where': {'id': group_id}, 'data': data}, query)
        if 'data' not in results:
            return results

    @cmd(name='get-mlflow', description='Get MLflow config from a group by id')
    def get_mlflow(self, group_id: str):
        """
        Get MLflow configuration from a group by id

        :type group_id: str
        :param group_id: group id
        :rtype dict
        :return MLflow configuration
        """
        query = """
        query GetGroupMLflowConfig($where: GroupWhereUniqueInput!) {
          group(where: $where) {
            id
            name
            mlflow {
              trackingUri
              uiUrl
              trackingEnvs {
                name
                value
              }
              artifactEnvs {
                name
                value
              }
            }
          }
        }
        """
        results = self.request({'where': {'id': group_id}}, query)
        if 'data' not in results:
            return results
        return results['data']['group']['mlflow']

    def help_description(self):
        return "Get a group or list groups"
