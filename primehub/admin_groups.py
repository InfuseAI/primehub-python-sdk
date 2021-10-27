import json
import re
from typing import Iterator, Union, Any

from primehub import Helpful, Module, cmd, primehub_load_config
from primehub.utils import PrimeHubException
from primehub.utils.optionals import file_flag, toggle_flag
from primehub.utils.validator import validate_groups


class AdminGroups(Helpful, Module):

    @cmd(name='list', description='List groups', return_required=True, optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator:
        """
        List groups

        :type page: int
        :param page: the page of all data

        :rtype Iterator
        :return group iterator
        """
        query = """
        query GroupsConnection($page: Int, $orderBy: GroupOrderByInput, $where: GroupWhereInput) {
          group: groupsConnection(page: $page, orderBy: $orderBy, where: $where) {
            edges {
              cursor
              node {
                ...GroupBasicInfo
              }
            }
            pageInfo {
              currentPage
              totalPage
            }
          }
        }
        
        fragment GroupBasicInfo on Group {
          id
          displayName
          name
          admins
          quotaCpu
          quotaGpu
          quotaMemory
          projectQuotaCpu
          projectQuotaGpu
          projectQuotaMemory
          sharedVolumeCapacity
        }
        """

        page = kwargs.get('page', 0)
        if page > 0:
            results = self.request({'page': page}, query)
            for e in results['data']['group']['edges']:
                yield e['node']
            return

        page = 1
        variables = {}
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['group']['edges']:
                for e in results['data']['group']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    def help_description(self):
        return "Manage groups"
