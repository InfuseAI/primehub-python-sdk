import json
import os
import time
from typing import Iterator, Any

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.utils import resource_not_found, PrimeHubException
from primehub.utils.optionals import toggle_flag, file_flag


def _error_handler(response):
    import re

    if 'errors' in response:
        message = [x for x in response['errors'] if 'message' in x]
        if message:
            message = message[0]['message']
            result = re.findall(r'phjobs.primehub.io "([^"]+)" not found', message)
            if result:
                resource_not_found('job', result[0], 'id')


def invalid_config(message: str):
    example = """
    {"instanceType":"cpu-1","image":"base-notebook","displayName":"job-example","command":"echo 'good job'"}
    """.strip()
    raise PrimeHubException(message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2))


def invalid_field(message: str):
    raise PrimeHubException(message)


def verify_basic_field(config: dict, for_update: bool = False):
    field_names = ['displayName', 'instanceType', 'image', 'command']

    for field_name in field_names:
        if field_name not in config:
            if for_update:
                continue
            invalid_config(f'{field_name} is required')

        field_val = config.get(field_name, '')
        if field_val is None or not isinstance(field_val, str):
            invalid_field(f'{field_name} should be string value')

        if field_val == '':
            invalid_field(f'{field_name} should be specified')


def verify_timeout(config: dict):
    field_name = 'activeDeadlineSeconds'
    if field_name not in config:
        return

    field_val = config.get(field_name, None)
    if field_val is None:
        invalid_field(f'{field_name} should not be empty')

    if not isinstance(field_val, int):
        invalid_field(f'{field_name} should be int value')


def rename_schedule_to_recurrence(message: dict):
    message['recurrence'] = message.pop('schedule', '')


class Jobs(Helpful, Module):
    """
    The jobs module provides functions to manage PrimeHub Jobs

    Job configuration example:
    {
        "instanceType": "cpu-1",
        "image": "base-notebook",
        "displayName": "test",
        "command": "echo \"test\""
    }
    """

    def _verify_dependency(self, config):
        if 'instanceType' in config:
            self.primehub.instancetypes.get(config['instanceType'])

    @cmd(name='list', description='List jobs', optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator[dict]:
        """
        List all job information in the current group

        :type page: int
        :param page: The page number as you can see in PrimeHub Jobs UI

        :rtype list
        :return The list of jobs
        """
        query = """
        query ($where: PhJobWhereInput, $page: Int, $orderBy: PhJobOrderByInput) {
          phJobsConnection(where: $where, page: $page, orderBy: $orderBy) {
            pageInfo {
              totalPage
              currentPage
            }
            edges {
              cursor
              node {
                id
                displayName
                cancel
                command
                groupId
                groupName
                schedule
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
                phase
                reason
                message
                createTime
                startTime
                finishTime
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
            for e in results['data']['phJobsConnection']['edges']:
                rename_schedule_to_recurrence(e['node'])
                yield e['node']
            return

        page = 1
        while True:
            variables['page'] = page
            results = self.request(variables, query)
            if results['data']['phJobsConnection']['edges']:
                for e in results['data']['phJobsConnection']['edges']:
                    rename_schedule_to_recurrence(e['node'])
                    yield e['node']
                page = page + 1
            else:
                break

    @cmd(name='get', description='Get a job by id', return_required=True)
    def get(self, id):
        """
        Get detail information of a job by id

        :type id: str
        :param id: The job id

        :rtype dict
        :return The detail information of a job
        """
        query = """
        query ($where: PhJobWhereUniqueInput!) {
          phJob(where: $where) {
            id
            displayName
            cancel
            command
            groupId
            groupName
            schedule
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
            phase
            reason
            message
            createTime
            startTime
            finishTime
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        rename_schedule_to_recurrence(results['data']['phJob'])

        return results['data']['phJob']

    @cmd(name='submit', description='Submit a job', optionals=[('file', file_flag), ('from', str)])
    def _submit_cmd(self, **kwargs):
        """
        Submit a job from commands

        :type file: str
        :param file: The file path of job configurations

        :type from: str
        :param from: The recurring job id to submit a job

        :rtype dict
        :return The detail information of the submitted job
        """
        if kwargs.get('from', None):
            return self.submit_from_recurring_job(kwargs['from'])

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('Job description is required.')

        config['groupId'] = self.group_id
        return self.submit(config)

    def submit(self, config):
        """
        Submit a job with config

        :type config: dict
        :param config: The job config

        :rtype dict
        :return The detail information of the submitted job
        """
        query = """
        mutation ($data: PhJobCreateInput!) {
          createPhJob(data: $data) {
            id
            displayName
            cancel
            command
            groupId
            groupName
            schedule
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
            phase
            reason
            message
            createTime
            startTime
            finishTime
          }
        }
        """

        if not config or (len(config) == 1):
            raise PrimeHubException('config is required')
        config['groupId'] = self.group_id

        # verify required fields in the config
        verify_basic_field(config)
        verify_timeout(config)

        self._verify_dependency(config)
        results = self.request({'data': config}, query)
        rename_schedule_to_recurrence(results['data']['createPhJob'])

        return results['data']['createPhJob']

    def submit_from_recurring_job(self, id):
        """
        Submit a job from the recurring job

        :type id: str
        :param id: The recurring job id

        :rtype dict
        :return The detail information of the submitted job
        """
        query = """
        mutation ($where: PhScheduleWhereUniqueInput!) {
          runPhSchedule(where: $where) {
            job {
              id
            }
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['runPhSchedule']

    @cmd(name='rerun', description='Rerun a job by id')
    def rerun(self, id):
        """
        Rerun a job by id

        :type id: str
        :param id: The job id

        :rtype dict
        :return The detail information of the ruran job
        """
        query = """
        mutation ($where: PhJobWhereUniqueInput!) {
          rerunPhJob(where: $where) {
            id
            displayName
            cancel
            command
            groupId
            groupName
            schedule
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
            phase
            reason
            message
            createTime
            startTime
            finishTime
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['rerunPhJob']

    @cmd(name='cancel', description='Cancel a job by id')
    def cancel(self, id):
        """
        Cancel a job by id

        :type id: str
        :param id: The job id

        :rtype dict
        :return The detail information of the canceled job
        """
        query = """
        mutation ($where: PhJobWhereUniqueInput!) {
          cancelPhJob(where: $where) {
            id
          }
        }
        """
        self.request({'where': {'id': id}}, query, _error_handler)
        return self.get(id)

    @cmd(name='wait', description='Wait a job by id', optionals=[('timeout', int)])
    def wait(self, id, **kwargs):
        """
        Wait a job in a terminated state {Succeeded, Failed, Cancelled} or until timeout

        :type id: str
        :param id: The job id

        :type timeout: int
        :param timeout: The timeout in second

        :rtype dict
        :return The detail information of the job
        """
        query = """
        query ($where: PhJobWhereUniqueInput!) {
          phJob(where: $where) {
            phase
          }
        }
        """
        timeout = kwargs.get('timeout', 0)
        start_time = time.time()
        while True:
            results = self.request({'where': {'id': id}}, query, _error_handler)
            phase = results['data']['phJob']['phase']
            if phase in ['Succeeded', 'Failed', 'Cancelled']:
                break
            time.sleep(1)
            if timeout != 0 and (time.time() - start_time >= timeout):
                break
        return self.get(id)

    @cmd(name='logs', description='Get job logs by id', optionals=[('follow', toggle_flag), ('tail', int)])
    def logs(self, id, **kwargs) -> Iterator[bytes]:
        """
        Get logs of a job

        :type id: str
        :param id: The job id

        :type follow: bool
        :param follow: Wait for additional logs to be appended

        :type tail: int
        :param tail: Show last n lines

        :rtype str
        :return The job logs
        """
        query = """
        query ($where: PhJobWhereUniqueInput!) {
          phJob(where: $where) {
            logEndpoint
          }
        }
        """

        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        results = self.primehub.request({'where': {'id': id}}, query, _error_handler)
        endpoint = results['data']['phJob']['logEndpoint']
        return self.primehub.request_logs(endpoint, follow, tail)

    @cmd(name='list-artifacts', description='List artifacts of a job by id')
    def list_artifacts(self, id):
        """
        List all artifacts of a job

        :type id: str
        :param id: The job id

        :rtype dict
        :return The detail information of the job artifacts
        """
        query = """
        query ($where: PhJobWhereUniqueInput!) {
          phJob(where: $where) {
            artifact {
              items {
                name
                size
                lastModified
              }
            }
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['phJob']['artifact']['items']

    @cmd(name='download-artifacts', description='Download artifacts', optionals=[('recursive', toggle_flag)])
    def download_artifacts(self, id, path, dest, **kwargs):
        """
        Download job artifacts

        :type id: str
        :param id: The job id

        :type path: str
        :param path: The path of job artifacts

        :type dest: str
        :param dest: The local path to save artifacts

        :type recursive: bool
        :param recursive: Copy recursively
        """

        if path in ['.', '', './']:
            path = '/'
        path = os.path.join('/jobArtifacts', id, path.lstrip('/'))

        # get id to verify existing
        self.get(id)
        self.primehub.files.download(path, dest, **kwargs)
        return

    def display(self, action: dict, value: Any):
        if action['func'] == 'list_artifacts' and isinstance(value, dict) and self.get_display().name != 'json':
            file_list = value.get('items', [])
            self.get_display().display(action, file_list, self.primehub.stdout)
        else:
            super(Jobs, self).display(action, value)

    def help_description(self):
        return "Manage jobs"
