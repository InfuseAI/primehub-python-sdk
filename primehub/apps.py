import json
from typing import Iterator, Any

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.utils import resource_not_found, PrimeHubException
from primehub.utils.display import display_tree_like_format
from primehub.utils.optionals import toggle_flag, file_flag

_query_ph_applications = query = """
        query PhApplicationsConnection(
            $where: PhApplicationWhereInput, $first: Int, $after: String, $last: Int, $before: String) {
            phApplicationsConnection(
              where: $where
              first: $first
              after: $after
              last: $last
              before: $before
            ) {
              pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
              }
              edges {
                cursor
                node {
                  ...PhApplicationInfo
                }
              }
            }
          }

          fragment PhApplicationInfo on PhApplication {
            id
            displayName
            appVersion
            appName
            appIcon
            appDefaultEnv {
              name
              defaultValue
              optional
              description
            }
            appTemplate {
              name
              docLink
              description
            }
            groupName
            instanceType
            instanceTypeSpec {
              name
              displayName
              cpuLimit
              memoryLimit
              gpuLimit
            }
            scope
            appUrl
            internalAppUrl
            svcEndpoints
            env {
              name
              value
            }
            stop
            status
            message
            pods {
              logEndpoint
            }
          }
        """
scope_list = ['public', 'primehub', 'group']


def _error_handler(response):
    import re

    if 'errors' in response:
        message = [x for x in response['errors'] if 'message' in x]
        if message:
            message = message[0]['message']
            result = re.findall(r'phapplications.primehub.io "([^"]+)" not found', message)
            if result:
                resource_not_found('phapplications', result[0], 'id')


def invalid_config(message: str):
    import uuid
    suffix = uuid.uuid4().hex[:5]
    example = """
    {"templateId":"code-server","id":"code-server-:id","displayName":"my-code-server-:id",
    "env":[{"name":"key1","value":"value1"}],"instanceType":"cpu-1","scope":"primehub"}
    """.strip().replace(':id', suffix)
    scope_help = f"""* the scope field could be one of the {scope_list}"""
    raise PrimeHubException(
        message + "\n\nExample:\n" + json.dumps(json.loads(example), indent=2) + f"\n\n{scope_help}\n")


class Apps(Helpful, Module):

    @cmd(name='create', description='Install an application', optionals=[('file', file_flag)])
    def _create(self, **kwargs):
        """
        Create a PrimeHub application

        :type file: str
        :param file: The file path of PrimeHub application configuration

        :rtype dict
        :return The information of the PrimeHub application
        """

        config = primehub_load_config(filename=kwargs.get('file', None))
        if not config:
            invalid_config('PrimeHub application configuration is required.')

        config['groupName'] = self.group_name
        return self.create(config)

    def create(self, config: dict):
        """
        Create a PrimeHub application

        :type config: dict
        :param config: The file path of PrimeHub application configuration

        :rtype dict
        :return The information of the PrimeHub application
        """
        query = """
        mutation CreatePhApplication($data: PhApplicationCreateInput!) {
          createPhApplication(data: $data) {
            id
          }
        }
        """

        if not config or (len(config) == 1):
            raise PrimeHubException('config is required')
        config['groupName'] = self.group_name

        # verify required fields in the config
        if 'instanceType' not in config:
            invalid_config('instanceType is required')
        if 'templateId' not in config:
            invalid_config('templateId is required')
        if 'displayName' not in config:
            invalid_config('displayName is required')
        if 'scope' not in config:
            invalid_config('scope is required')
        else:
            if config['scope'] not in scope_list:
                invalid_config('scope is invalid')

        if 'env' in config:
            if not isinstance(config['env'], list):
                invalid_config('env should be a list of the name and value pair')
            for x in config['env']:
                if not isinstance(x, dict):
                    invalid_config('entry in the "env" should be a name and value pair')
                valid = 'name' in x and 'value' in x
                if not valid:
                    invalid_config('entry in the "env" should be a name and value pair')
                if not isinstance(x['value'], str):
                    invalid_config(f'value in an entry must be the string type => {x}')

        self._verify_dependency(config)
        results = self.request({'data': config}, query)
        if 'data' in results:
            return results['data']['createPhApplication']
        return results

    def _verify_dependency(self, config):
        if 'instanceType' in config:
            self.primehub.instancetypes.get(config['instanceType'])

    @cmd(name='list', description='List PrimeHub Applications', return_required=True)
    def list(self) -> Iterator:
        """
        List PrimeHub applications

        :rtype: Iterator
        :returns: PrimeHub applications
        """
        page_size = 12
        variables = {'where': {'groupName_in': [self.group_name]}}
        results = self.request({'first': page_size, **variables}, _query_ph_applications)

        while True:
            for e in results['data']['phApplicationsConnection']['edges']:
                yield e['node']

            has_next_page = results['data']['phApplicationsConnection']['pageInfo']['hasNextPage']
            if not has_next_page:
                return

            next_token = results['data']['phApplicationsConnection']['pageInfo']['endCursor']
            results = self.request({'first': page_size, 'after': next_token, **variables}, _query_ph_applications)

    @cmd(name='get', description='Get the PrimeHub Application', return_required=True)
    def get(self, id) -> dict:
        """
        Get the PrimeHub application by id

        :rtype: Iterator
        :returns: a PrimeHub application
        """

        page_size = 12
        variables = {'where': {'groupName_in': [self.group_name], 'id': id}}
        results = self.request({'first': page_size, **variables}, _query_ph_applications)

        edges = results['data']['phApplicationsConnection']['edges']
        return edges[0]['node']

    @cmd(name='stop', description='Stop the PrimeHub Application', return_required=True)
    def stop(self, id) -> dict:
        """
        Stop the PrimeHub application by id

        :rtype: dict
        :returns: a PrimeHub application
        """

        query = """
        mutation StopPhApplication($where: PhApplicationWhereUniqueInput!) {
          stopPhApplication(where: $where) {
            ...PhApplicationInfo
          }
        }

        fragment PhApplicationInfo on PhApplication {
          id
          displayName
          appVersion
          appName
          appIcon
          appDefaultEnv {
            name
            defaultValue
            optional
            description
          }
          appTemplate {
            name
            docLink
            description
          }
          groupName
          instanceType
          instanceTypeSpec {
            name
            displayName
            cpuLimit
            memoryLimit
            gpuLimit
          }
          scope
          appUrl
          internalAppUrl
          svcEndpoints
          env {
            name
            value
          }
          stop
          status
          message
          pods {
            logEndpoint
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        if 'data' in results and 'stopPhApplication' in results['data']:
            return results['data']['stopPhApplication']
        return results

    @cmd(name='start', description='Start the PrimeHub Application', return_required=True)
    def start(self, id) -> dict:
        """
        Start the PrimeHub application by id

        :rtype: dict
        :returns: a PrimeHub application
        """

        query = """
        mutation StartPhApplication($where: PhApplicationWhereUniqueInput!) {
            startPhApplication(where: $where) {
              ...PhApplicationInfo
            }
          }

          fragment PhApplicationInfo on PhApplication {
            id
            displayName
            appVersion
            appName
            appIcon
            appDefaultEnv {
              name
              defaultValue
              optional
              description
            }
            appTemplate {
              name
              docLink
              description
            }
            groupName
            instanceType
            instanceTypeSpec {
              name
              displayName
              cpuLimit
              memoryLimit
              gpuLimit
            }
            scope
            appUrl
            internalAppUrl
            svcEndpoints
            env {
              name
              value
            }
            stop
            status
            message
            pods {
              logEndpoint
            }
          }
        """
        results = self.request({'where': {'id': id}}, query)
        if 'data' in results and 'startPhApplication' in results['data']:
            return results['data']['startPhApplication']
        return results

    @cmd(name='delete', description='Stop the PrimeHub Application', return_required=True)
    def delete(self, id) -> dict:
        """
        Uninstall the PrimeHub application by id

        :rtype: dict
        :returns: a PrimeHub application
        """

        query = """
        mutation DeletePhApplication($where: PhApplicationWhereUniqueInput!) {
          deletePhApplication(where: $where) {
            ...PhApplicationInfo
          }
        }

        fragment PhApplicationInfo on PhApplication {
          id
          displayName
          appVersion
          appName
          appIcon
          appDefaultEnv {
            name
            defaultValue
            optional
            description
          }
          appTemplate {
            name
            docLink
            description
          }
          groupName
          instanceType
          instanceTypeSpec {
            name
            displayName
            cpuLimit
            memoryLimit
            gpuLimit
          }
          scope
          appUrl
          internalAppUrl
          svcEndpoints
          env {
            name
            value
          }
          stop
          status
          message
          pods {
            logEndpoint
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        if 'data' in results and 'deletePhApplication' in results['data']:
            return results['data']['deletePhApplication']
        return results

    @cmd(name='logs', description='Get logs of the PrimeHub Application by id',
         optionals=[('follow', toggle_flag), ('tail', int)])
    def logs(self, id, **kwargs) -> Iterator[bytes]:
        """
        Get logs of the PrimeHub application

        :type id: str
        :param id: The job id

        :type follow: bool
        :param follow: Wait for additional logs to be appended

        :type tail: int
        :param tail: Show last n lines

        :rtype str
        :return logs stream
        """

        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        results = self.get(id)

        # for now, there is the only one pod in the PrimeHub application
        if 'pods' in results and results['pods']:
            endpoint = results['pods'][0]['logEndpoint']
            return self.primehub.request_logs(endpoint, follow, tail)

        return results

    def help_description(self):
        return "Manage PrimeHub Applications"

    def display(self, action: dict, value: Any):
        single_results = [Apps.get.__name__, Apps.start.__name__, Apps.stop.__name__, Apps.delete.__name__]

        # customize the list view from columns to tree-like
        if action['func'] == Apps.list.__name__ and self.get_display().name != 'json':
            for template in value:
                template = self.convert_for_human_friendly_data(template)
                display_tree_like_format(template, file=self.primehub.stdout)
                print("", file=self.primehub.stdout)
        elif action['func'] in single_results and self.get_display().name != 'json':
            super(Apps, self).display(action, self.convert_for_human_friendly_data(value))
        else:
            super(Apps, self).display(action, value)

    def convert_for_human_friendly_data(self, app):
        app.pop('appIcon')
        return app
