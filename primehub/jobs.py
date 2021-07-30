from typing import Iterator

from primehub import Helpful, cmd, Module, has_data_from_stdin
import time
import os
import json
import sys
from urllib.parse import urlparse


class Jobs(Helpful, Module):

    @cmd(name='list', description='List jobs', optionals=[('page', int)])
    def list(self, **kwargs):
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
                'groupId_in': [self.primehub_config.group_info['id']]
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
    def submit(self, **kwargs):
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
        if kwargs.get('from', None):
            return self.submit_from_schedule(kwargs['from'])

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
        return results['data']['createPhJob']

    def submit_from_schedule(self, id):
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
    @cmd(name='cancel', description='Cnacel a job by id')
    def cancel(self, id):
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
    @cmd(name='download-artifacts', description='Download artifacts', optionals=[('recursive', bool)])
    def download_artifacts(self, id, path, dest, **kwargs):
        artifacts = self.list_artifacts(id)
        u = urlparse(self.primehub_config.endpoint)
        endpoint = u._replace(path='/api/files/' + artifacts['prefix'] + '/').geturl()

        if dest[-1] != '/':
            dest = dest + '/'

        if kwargs.get('recursive', False):
            if path[-1] != '/':     # avoid files or directories with the same prefix
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
