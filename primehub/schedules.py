from primehub import Helpful, cmd, Module, has_data_from_stdin
import os
import json
import sys


class Schedules(Helpful, Module):

    # TODO: add page argument
    @cmd(name='list', description='List schedules')
    def list(self):
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
        edges = []
        variables = {
          'where': {
            'groupId_in': [self.primehub_config.group_info['id']]
          },
          'page': 1
        }
        while True:
            results = self.request(variables, query)
            if results['data']['phSchedulesConnection']['edges']:
                edges.extend(results['data']['phSchedulesConnection']['edges'])
                variables['page'] = variables['page'] + 1
            else:
                break
        return edges

    @cmd(name='get', description='Get a schedule by id')
    def get(self, schedule_id):
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
        results = self.request({'where': {'id': schedule_id}}, query)
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
        data['groupId'] = self.primehub_config.group_info['id']
        results = self.request({'data': data}, query)
        return results['data']['createPhSchedule']

    # TODO: add -f
    # TODO: handel invalid config
    @cmd(name='update', description='Update a schedule by id', optionals=[('file', str)])
    def update(self, job_id, **kwargs):
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
        data['groupId'] = self.primehub_config.group_info['id']
        results = self.request({'data': data, 'where': {'id': job_id}}, query)
        return results['data']['updatePhSchedule']

    # TODO: add optionals=[('yes-i-really-mean-it', bool)]
    @cmd(name='delete', description='Run a schedule by id')
    def delete(self, schedule_id, **kwargs):
        query = """
        mutation ($where: PhScheduleWhereUniqueInput!) {
          deletePhSchedule(where: $where) {
            id
          }
        }
        """
        # valid = kwargs.get('yes-i-really-mean-it', False)
        # if not valid:
        #     return 'Delete a schedule by passing --yes-i-really-mean-it flag'
        results = self.request({'where': {'id': schedule_id}}, query)
        return results['data']['deletePhSchedule']

    def help_description(self):
        return "Get a schedule or list schedules"
