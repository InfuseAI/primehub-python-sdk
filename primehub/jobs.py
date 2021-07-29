from primehub import Helpful, cmd, Module, has_data_from_stdin
import time
import os
import json
import sys


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
    def get(self, job_id):
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
        results = self.request({'where': {'id': job_id}}, query)
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

    def submit_from_schedule(self, schedule_id):
        query = """
        mutation ($where: PhScheduleWhereUniqueInput!) {
          runPhSchedule(where: $where) {
            job {
              id
            }
          }
        }
        """
        results = self.request({'where': {'id': schedule_id}}, query)
        return results['data']['runPhSchedule']

    # TODO: handel id does not exist
    @cmd(name='rerun', description='Rerun a job by id')
    def rerun(self, job_id):
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
        results = self.request({'where': {'id': job_id}}, query)
        return results['data']['rerunPhJob']

    # TODO: handel id does not exist
    @cmd(name='cancel', description='Cnacel a job by id')
    def cancel(self, job_id):
        query = """
        mutation ($where: PhJobWhereUniqueInput!) {
          cancelPhJob(where: $where) {
            id
          }
        }
        """
        self.request({'where': {'id': job_id}}, query)
        return self.get(job_id)

    @cmd(name='wait', description='Wait a job by id', optionals=[('timeout', int)])
    def wait(self, job_id, **kwargs):
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
            results = self.request({'where': {'id': job_id}}, query)
            phase = results['data']['phJob']['phase']
            if phase in ['Succeeded', 'Failed', 'Cancelled']:
                break
            time.sleep(1)
            if timeout != 0 and (time.time() - start_time >= timeout):
                break
        return self.get(job_id)

    @cmd(name='log', description='Get job log by id', optionals=[('follow', bool), ('tail', int)])
    def log(self, job_id, **kwargs):
        query = """
        query ($where: PhJobWhereUniqueInput!) {
          phJob(where: $where) {
            logEndpoint
          }
        }
        """

        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        results = self.request({'where': {'id': job_id}}, query)
        endpoint = results['data']['phJob']['logEndpoint']
        response = self.request_logs(endpoint, follow, tail)
        if follow:
            try:
                for s in response.iter_lines():
                    print(s.decode())
            finally:
                response.close()
                return
        return response.text

    def help_description(self):
        return "Get a job or list jobs"
