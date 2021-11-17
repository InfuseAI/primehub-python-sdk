import json
from typing import Iterator

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.utils import resource_not_found, PrimeHubException
from primehub.utils.optionals import file_flag
from primehub.utils.permission import ask_for_permission
from primehub.jobs import verify_basic_field, verify_timeout, invalid_field


def _error_handler(response):
    import re

    if 'errors' in response:
        message = [x for x in response['errors'] if 'message' in x]
        if message:
            message = message[0]['message']
            result = re.findall(r'phschedules.primehub.io "([^"]+)" not found', message)
            if result:
                resource_not_found('recurring-jobs', result[0], 'id')


def invalid_config(message: str):
    example = """
    {"instanceType":"cpu-1","image":"base-notebook","displayName":"recurring-job-example","command":"echo 'good job'","recurrence":{"type":"daily","cron":"0 4 * * *"}}
    """.strip()  # noqa: E501
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def verify_recurrence_options(config: dict):
    type_options = ['on-demand', 'daily', 'weekly', 'monthly', 'custom']

    type_option = config.get('type', '')
    if not type_option:
        invalid_config('type is required')
    if not isinstance(type_option, str):
        invalid_field('type should be string value')
    if type_option not in type_options:
        invalid_field(f'\'{type_option}\' is not acceptable type')

    cron_val = config.get('cron', '')
    if not isinstance(cron_val, str):
        invalid_field('cron should be string value')

    if type_option == 'custom' and not cron_val:
        invalid_config('cron is required in custom type')

    if type_option != 'custom' and cron_val != '':
        print('Notice: To make cron you defined effective, please use \'custom\' type')


def verify_recurrence(config: dict, for_update: bool = False):
    field_name = 'recurrence'
    if field_name not in config:
        if for_update:
            return
        invalid_config(f'{field_name} is required')

    field_val = config.get(field_name, None)
    if field_val is None or not isinstance(field_val, dict):
        invalid_field(f'{field_name} should be a json object')

    verify_recurrence_options(field_val)


def verify_config(config: dict, for_update: bool = False):
    verify_basic_field(config, for_update)
    verify_timeout(config)
    verify_recurrence(config, for_update)


def rename_inactive_to_on_demand_when_read(message: dict):
    if message['recurrence']['type'] == 'inactive':
        message['recurrence']['type'] = 'on-demand'


def rename_on_demand_to_inactive_when_write(config: dict):
    recurrence_type = config['recurrence'].get('type', '')
    if recurrence_type == 'on-demand':
        config['recurrence']['type'] = 'inactive'


class RecurringJobs(Helpful, Module):
    """
    The recurring jobs module provides functions to manage PrimeHub RecurringJobs

    Recurring job configuration example:
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

    @cmd(name='list', description='List recurring jobs', optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator[dict]:
        """
        List all recurring jobs information in the current group

        :type page: int
        :param page: The page number as you can see in PrimeHub RecurringJobs UI

        :rtype list
        :return The list of recurring jobs
        """
        query = """
        query (
          $where: PhScheduleWhereInput
          $page: Int
          $orderBy: PhScheduleOrderByInput
        ) {
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
                rename_inactive_to_on_demand_when_read(e['node'])
                yield e['node']
            return

        page = 1
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['phSchedulesConnection']['edges']:
                for e in results['data']['phSchedulesConnection']['edges']:
                    rename_inactive_to_on_demand_when_read(e['node'])
                    yield e['node']
                page = page + 1
            else:
                break

    @cmd(name='get', description='Get a recurring job by id', return_required=True)
    def get(self, id):
        """
        Get detail information of a recurring job by id

        :type id: str
        :param id: The recurring job id

        :rtype dict
        :return The detail information of a recurring job
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
        rename_inactive_to_on_demand_when_read(results['data']['phSchedule'])

        return results['data']['phSchedule']

    @cmd(name='create', description='Create a recurring job', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Submit a recurring job from commands

        :type file: str
        :param file: The file path of recurring job configurations

        :rtype dict
        :return The detail information of the created recurring job
        """
        config = primehub_load_config(filename=kwargs.get('file', None))

        if not config:
            invalid_config('Recurring job description is required.')

        return self.create(config)

    def create(self, config):
        """
        Create a recurring jobs with config

        :type config: dict
        :param config: The recurring job config

        :rtype dict
        :return The detail information of the created recurring job
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
        rename_on_demand_to_inactive_when_write(config)
        results = self.request({'data': config}, query)
        rename_inactive_to_on_demand_when_read(results['data']['createPhSchedule'])
        return results['data']['createPhSchedule']

    @cmd(name='update', description='Update a recurring job by id', optionals=[('file', file_flag)])
    def _update_cmd(self, id, **kwargs):
        """
        Update a recurring job from commands

        :type file: str
        :param file: The file path of recurring job configurations

        :rtype dict
        :return The detail information of the updated recurring job
        """
        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('Recurring job description is required.')

        return self.update(id, config)

    def update(self, id, config):
        """
        Update a recurring job with config

        :type id: str
        :param id: The recurring job id

        :type config: dict
        :param config: The recurring job config

        :rtype dict
        :return The detail information of the updated recurring job
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
        verify_config(config, True)
        self._verify_dependency(config)
        if 'recurrence' in config:
            rename_on_demand_to_inactive_when_write(config)

        results = self.request({'data': config, 'where': {'id': id}}, query, _error_handler)
        rename_inactive_to_on_demand_when_read(results['data']['updatePhSchedule'])
        return results['data']['updatePhSchedule']

    @ask_for_permission
    @cmd(name='delete', description='Delete a recurring job by id')
    def delete(self, id, **kwargs):
        """
        Delete a recurring job by id

        :type id: str
        :param id: The recurring job id

        :rtype dict
        :return The detail information of the deleted recurring job
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
        return "Manage recurring jobs"
