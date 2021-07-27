from primehub import Helpful, cmd, Module


class Jobs(Helpful, Module):
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

    # TODO: add page argument
    @cmd(name='list', description='List jobs')
    def list(self):
        edges = []
        variables = {
          'where': {
            'groupId_in': [self.primehub_config.group_info['id']]
          },
          'page': 1
        }
        while True:
            results = self.request(variables, Jobs.query)
            if results['data']['phJobsConnection']['edges']:
                edges.extend(results['data']['phJobsConnection']['edges'])
                variables['page'] = variables['page'] + 1
            else:
                break
        return edges

    @cmd(name='get', description='Get job by id')
    def get(self, job_id):
        variables = {
          'where': {
            'groupId_in': [self.primehub_config.group_info['id']],
            'id': job_id
          },
        }
        results = self.request(variables, Jobs.query)
        return results['data']['phJobsConnection']['edges']

    def help_description(self):
        return "Get a job or list jobs"
