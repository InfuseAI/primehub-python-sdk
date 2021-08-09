from typing import Iterator

from primehub import Helpful, cmd, Module, has_data_from_stdin
import time
import os
import json
import sys
from urllib.parse import urlparse

from primehub.utils.optionals import toggle_flag


class Jobs(Helpful, Module):
    """
    The jobs module provides functions to manage PrimeHub Jobs

    Job configuration example:
    {
        "instanceType": "cpu-1",
        "image": "base-notebook",
        "displayName": "test",
        "command": "echo \"test\"",
    }
    """

    @cmd(name='list', description='List jobs', optionals=[('page', int)])
    def list(self, **kwargs):
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
        variables = {
            'where': {
                'groupId_in': [self.group_id]
            },
            'page': 1
        }
        if kwargs.get('page', None):
            variables['page'] = kwargs['page']
            results = self.request(variables, query)
            return [e['node'] for e in results['data']['phJobsConnection']['edges']]

        edges = []
        while True:
            results = self.request(variables, query)
            if results['data']['phJobsConnection']['edges']:
                edges.extend([e['node'] for e in results['data']['phJobsConnection']['edges']])
                variables['page'] = variables['page'] + 1
            else:
                break
        return edges

    @cmd(name='get', description='Get a job by id')
    def get(self, id):
        """
        Get detail information of a job by id

        :type id: str
        :param id: The job id

        :rtype dict
        :return The detail infromation of a job
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
        results = self.request({'where': {'id': id}}, query)
        return results['data']['phJob']

    # TODO: add -f
    # TODO: handel invalid config
    @cmd(name='submit', description='Submit a job', optionals=[('file', str), ('from', str)])
    def submit_cmd(self, **kwargs):
        """
        Submit a job from commands

        :type file: str
        :param file: The file path of job configurations

        :type from: str
        :param from: The schedule id to submit as a job

        :rtype dict
        :return The detail infromation of the submitted job
        """
        if kwargs.get('from', None):
            return self.submit_from_schedule(kwargs['from'])

        config = {}
        filename = kwargs.get('file', None)
        if filename and os.path.exists(filename):
            with open(filename, 'r') as fh:
                config = json.load(fh)

        if has_data_from_stdin():
            config = json.loads("".join(sys.stdin.readlines()))

        config['groupId'] = self.group_id
        return self.submit(config)

    # TODO: Add validation for config
    def submit(self, config):
        """
        Submit a job with config

        :type config: dict
        :param config: The job config

        :rtype dict
        :return The detail infromation of the submitted job
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
        config['groupId'] = self.group_id
        results = self.request({'data': config}, query)
        return results['data']['createPhJob']

    def submit_from_schedule(self, id):
        """
        Submit a job from schedules

        :type id: str
        :param id: The schedule id

        :rtype dict
        :return The detail infromation of the submitted job
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
        results = self.request({'where': {'id': id}}, query)
        return results['data']['runPhSchedule']

    # TODO: handel id does not exist
    @cmd(name='rerun', description='Rerun a job by id')
    def rerun(self, id):
        """
        Rerun a job by id

        :type id: str
        :param id: The job id

        :rtype dict
        :return The detail infromation of the ruran job
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
        results = self.request({'where': {'id': id}}, query)
        return results['data']['rerunPhJob']

    # TODO: handel id does not exist
    @cmd(name='cancel', description='Cancel a job by id')
    def cancel(self, id):
        """
        Cancle a job by id

        :type id: str
        :param id: The job id

        :rtype dict
        :return The detail infromation of the canceled job
        """
        query = """
        mutation ($where: PhJobWhereUniqueInput!) {
          cancelPhJob(where: $where) {
            id
          }
        }
        """
        self.request({'where': {'id': id}}, query)
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
        :return The detail infromation of the job
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
            results = self.request({'where': {'id': id}}, query)
            phase = results['data']['phJob']['phase']
            if phase in ['Succeeded', 'Failed', 'Cancelled']:
                break
            time.sleep(1)
            if timeout != 0 and (time.time() - start_time >= timeout):
                break
        return self.get(id)

    @cmd(name='logs', description='Get job logs by id', optionals=[('follow', bool), ('tail', int)])
    def logs(self, id, **kwargs) -> Iterator[str]:
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

        results = self.primehub.request({'where': {'id': id}}, query)
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
              prefix
              items {
                name
                size
                lastModified
              }
            }
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        return results['data']['phJob']['artifact']

    # TODO: handel path or dest does not exist
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

        :type recusive: bool
        :param recusive: Copy recursively
        """
        artifacts = self.list_artifacts(id)
        u = urlparse(self.endpoint)
        endpoint = u._replace(path='/api/files/' + artifacts['prefix'] + '/').geturl()

        if dest[-1] != '/':
            dest = dest + '/'

        if kwargs.get('recursive', False):
            if path[-1] != '/':  # avoid files or directories with the same prefix
                path = path + '/'
            dirname = os.path.dirname(path[:-1])
            paths = [e['name'] for e in artifacts['items'] if e['name'].startswith(path)]
            for p in paths:
                self.request_file(endpoint + p, dest + p[len(dirname):])
            return
        self.request_file(endpoint + path, dest + os.path.basename(path))
        return

    def help_description(self):
        return "Get a job or list jobs"
