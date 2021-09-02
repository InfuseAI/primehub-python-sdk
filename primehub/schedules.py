import json
from typing import Iterator

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.utils import resource_not_found, PrimeHubException
from primehub.utils.optionals import file_flag
from primehub.utils.permission import ask_for_permission


def _error_handler(response):
    import re

    if 'errors' in response:
        message = [x for x in response['errors'] if 'message' in x]
        if message:
            message = message[0]['message']
            result = re.findall(r'phschedules.primehub.io "([^"]+)" not found', message)
            if result:
                resource_not_found('schedule', result[0], 'id')


def invalid_config(message: str):
    example = """
    {"instanceType":"cpu-1","image":"base-notebook","displayName":"schedule-example","command":"echo 'good job'","recurrence":{"type":"daily","cron":"0 4 * * *"}}
    """.strip()  # noqa: E501
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def verify_config(config):
    # verify required fields in the config
    if 'instanceType' not in config:
        invalid_config('instanceType is required')
    if 'image' not in config:
        invalid_config('image is required')
    if 'displayName' not in config:
        invalid_config('displayName is required')
    if 'command' not in config:
        invalid_config('command is required')
    if 'recurrence' not in config:
        invalid_config('recurrence is required')


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

    def _verify_dependency(self, config):
        if 'instanceType' in config:
            self.primehub.instancetypes.get(config['instanceType'])

    @cmd(name='list', description='List schedules', optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator[dict]:
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
        variables = {'where': {'groupId_in': [self.group_id]}, 'page': 1}
        page = kwargs.get('page', 0)
        if page:
            variables['page'] = page
            results = self.request(variables, query)
            for e in results['data']['phSchedulesConnection']['edges']:
                yield e['node']
            return

        page = 1
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['phSchedulesConnection']['edges']:
                for e in results['data']['phSchedulesConnection']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    @cmd(name='get', description='Get a schedule by id', return_required=True)
    def get(self, id):
        """
        Get detail information of a schedule by id

        :type id: str
        :param id: The schedule id

        :rtype dict
        :return The detail information of a schedule
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
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['phSchedule']

    @cmd(name='create', description='Create a schedule', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Submit a schedule from commands

        :type file: str
        :param file: The file path of schedule configurations

        :rtype dict
        :return The detail information of the created schedule
        """
        config = primehub_load_config(filename=kwargs.get('file', None))

        if not config:
            invalid_config('Schedule description is required.')

        return self.create(config)

    def create(self, config):
        """
        Create a schedules with config

        :type config: dict
        :param config: The schedule config

        :rtype dict
        :return The detail information of the created schedule
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

        verify_config(config)
        self._verify_dependency(config)
        results = self.request({'data': config}, query)
        return results['data']['createPhSchedule']

    @cmd(name='update', description='Update a schedule by id', optionals=[('file', file_flag)])
    def _update_cmd(self, id, **kwargs):
        """
        Update a schedule from commands

        :type file: str
        :param file: The file path of schedule configurations

        :rtype dict
        :return The detail information of the updated schedule
        """
        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('Schedule description is required.')

        return self.update(id, config)

    def update(self, id, config):
        """
        Update a schedule with config

        :type id: str
        :param id: The schedule id

        :type config: dict
        :param config: The schedule config

        :rtype dict
        :return The detail information of the updated schedule
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
        if not config:
            invalid_config('Schedule description is required.')
        self._verify_dependency(config)
        results = self.request({'data': config, 'where': {'id': id}}, query, _error_handler)
        return results['data']['updatePhSchedule']

    @ask_for_permission
    @cmd(name='delete', description='Delete a schedule by id')
    def delete(self, id, **kwargs):
        """
        Delete a schedule by id

        :type id: str
        :param id: The schedule id

        :rtype dict
        :return The detail information of the deleted schedule
        """
        query = """
        mutation ($where: PhScheduleWhereUniqueInput!) {
          deletePhSchedule(where: $where) {
            id
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['deletePhSchedule']

    def help_description(self):
        return "Get a schedule or list schedules"
