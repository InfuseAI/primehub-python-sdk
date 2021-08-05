from primehub import Helpful, cmd, Module, has_data_from_stdin
from primehub.utils.permission import ask_for_permission
import os
import json
import sys


class Schedules(Helpful, Module):
    """
    The schedules module provides functions to manage PrimeHub Schedules

    Schedule configuration example:
    {
        "instanceType": "cpu-1",
        "image": "base-notebook",
        "displayName": "test",
        "command": "echo \"test\"",
        "recurrence": {
            "type":"daily",
            "cron":"0 4 * * *"
        }
    }
    """

    @cmd(name='list', description='List schedules', optionals=[('page', int)])
    def list(self, **kwargs):
        """
        List all schedules information in the current group

        :type page: int
        :param page: The page number as you can see in PrimeHub Schedules UI

        :rtype list
        :return The list of schedules
        """
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
        """
        Get detail information of a schedule by id

        :type id: str
        :param id: The schedule id

        :rtype dict
        :return The detail infromation of a schedule
        """
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
    def create_cmd(self, **kwargs):
        """
        Submit a schedule from commands

        :type file: str
        :param file: The file path of schedule configurations

        :rtype dict
        :return The detail infromation of the created schedule
        """
        config = {}
        filename = kwargs.get('file', None)
        if filename and os.path.exists(filename):
            with open(filename, 'r') as fh:
                config = json.load(fh)

        if has_data_from_stdin():
            config = json.loads("".join(sys.stdin.readlines()))

        return self.create(config)

    # TODO: add validation for config
    def create(self, config):
        """
        Create a schedules with config

        :type config: dict
        :param config: The schedule config

        :rtype dict
        :return The detail infromation of the created schedule
        """
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
        config['groupId'] = self.group_id
        results = self.request({'data': config}, query)
        return results['data']['createPhSchedule']

    # TODO: add -f
    # TODO: handel invalid config
    @cmd(name='update', description='Update a schedule by id', optionals=[('file', str)])
    def update_cmd(self, id, **kwargs):
        """
        Update a schedule from commands

        :type file: str
        :param file: The file path of schedule configurations

        :rtype dict
        :return The detail infromation of the updated schedule
        """
        config = {}
        filename = kwargs.get('file', None)
        if filename and os.path.exists(filename):
            with open(filename, 'r') as fh:
                config = json.load(fh)

        if has_data_from_stdin():
            config = json.loads("".join(sys.stdin.readlines()))

        return self.update(id, config)

    # TODO: add validation for config
    def update(self, id, config):
        """
        Update a schedule with config

        :type id: str
        :param id: The schedule id

        :type config: dict
        :param config: The schedule config

        :rtype dict
        :return The detail infromation of the updated schedule
        """
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
        config['groupId'] = self.group_id
        results = self.request({'data': config, 'where': {'id': id}}, query)
        return results['data']['updatePhSchedule']

    @ask_for_permission
    @cmd(name='delete', description='Delete a schedule by id')
    def delete(self, id, **kwargs):
        """
        Delete a schedule by id

        :type id: str
        :param id: The schedule id

        :rtype dict
        :return The detail infromation of the deleted schedule
        """
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
