from primehub import Helpful, cmd, Module, has_data_from_stdin
from primehub.utils.permission import ask_for_permission
import os
import json
import sys


class Schedules(Helpful, Module):

    @cmd(name='list', description='List schedules', optionals=[('page', int)])
    def list(self, **kwargs):
        query = """
        query ($where: PhScheduleWhereInput, $page: Int, $orderBy: PhScheduleOrderByInput) {
          phSchedulesConnection(where: $where, page: $page, orderBy: $orderBy) {
            pageInfo {
              totalPage
              currentPage
            }
            edges {
              cursor
              node {
                id
                displayName
                recurrence {
                  type
                  cron
                }
                invalid
                message
                command
                groupId
                groupName
                image
                instanceType {
                  id
                  name
                  displayName
                  cpuLimit
                  memoryLimit
                  gpuLimit
                }
                userId
                userName
                nextRunTime
              }
            }
          }
        }
        """
        variables = {
          'where': {
            'groupId_in': [self.group_id]
          },
          'page': 1
        }
        if kwargs.get('page', None):
            variables['page'] = kwargs['page']
            results = self.request(variables, query)
            return [e['node'] for e in results['data']['phSchedulesConnection']['edges']]

        edges = []
        while True:
            results = self.request(variables, query)
            if results['data']['phSchedulesConnection']['edges']:
                edges.extend([e['node'] for e in results['data']['phSchedulesConnection']['edges']])
                variables['page'] = variables['page'] + 1
            else:
                break
        return edges

    @cmd(name='get', description='Get a schedule by id')
    def get(self, id):
        query = """
        query ($where: PhScheduleWhereUniqueInput!) {
          phSchedule(where: $where) {
            id
            displayName
            recurrence {
              type
              cron
            }
            invalid
            message
            command
            groupId
            groupName
            image
            instanceType {
              id
              name
              displayName
              cpuLimit
              memoryLimit
              gpuLimit
            }
            userId
            userName
            nextRunTime
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        return results['data']['phSchedule']

    # TODO: add -f
    # TODO: handel invalid config
    @cmd(name='create', description='Create a schedule', optionals=[('file', str)])
    def create(self, **kwargs):
        query = """
        mutation ($data: PhScheduleCreateInput!) {
          createPhSchedule(data: $data) {
            id
            displayName
            recurrence {
              type
              cron
            }
            invalid
            message
            command
            groupId
            groupName
            image
            instanceType {
              id
              name
              displayName
              cpuLimit
              memoryLimit
              gpuLimit
            }
            userId
            userName
            nextRunTime
          }
        }
        """
        data = {}
        if has_data_from_stdin():
            data = json.loads("".join(sys.stdin.readlines()))
        else:
            filename = kwargs.get('file', None)
            print(filename)
            if os.path.exists(filename):
                with open(filename, 'r') as fh:
                    data = json.load(fh)
        data['groupId'] = self.group_id
        results = self.request({'data': data}, query)
        return results['data']['createPhSchedule']

    # TODO: add -f
    # TODO: handel invalid config
    @cmd(name='update', description='Update a schedule by id', optionals=[('file', str)])
    def update(self, id, **kwargs):
        query = """
        mutation ($data: PhScheduleUpdateInput!, $where: PhScheduleWhereUniqueInput!) {
          updatePhSchedule(data: $data, where: $where) {
            id
            displayName
            recurrence {
              type
              cron
            }
            invalid
            message
            command
            groupId
            groupName
            image
            instanceType {
              id
              name
              displayName
              cpuLimit
              memoryLimit
              gpuLimit
            }
            userId
            userName
            nextRunTime
          }
        }
        """
        data = {}
        if has_data_from_stdin():
            data = json.loads("".join(sys.stdin.readlines()))
        else:
            filename = kwargs.get('file', None)
            print(filename)
            if os.path.exists(filename):
                with open(filename, 'r') as fh:
                    data = json.load(fh)
        data['groupId'] = self.group_id
        results = self.request({'data': data, 'where': {'id': id}}, query)
        return results['data']['updatePhSchedule']

    @ask_for_permission
    @cmd(name='delete', description='Run a schedule by id')
    def delete(self, id, **kwargs):
        query = """
        mutation ($where: PhScheduleWhereUniqueInput!) {
          deletePhSchedule(where: $where) {
            id
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        return results['data']['deletePhSchedule']

    def help_description(self):
        return "Get a schedule or list schedules"
