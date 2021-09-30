import json
import time
from typing import Iterator

from primehub import Helpful, cmd, Module, primehub_load_config
from primehub.utils import resource_not_found, PrimeHubException
from primehub.utils.optionals import toggle_flag, file_flag
from primehub.utils.permission import ask_for_permission


def _error_handler(response):
    import re

    if 'errors' in response:
        message = [x for x in response['errors'] if 'message' in x]
        if message:
            message = message[0]['message']
            result = re.findall(r'phdeployments.primehub.io "([^"]+)" not found', message)
            if result:
                resource_not_found('schedule', result[0], 'id')


def invalid_config(message: str):
    import random
    import string
    import textwrap

    id = 'quickstart-iris-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    example = """
    {"name":"quickstart-iris","modelImage":"infuseai/sklearn-prepackaged:v0.1.0","modelURI":"gs://seldon-models/sklearn/iris","env":[],"metadata":{},"instanceType":"cpu-1","replicas":1,"updateMessage":"","id":"<id>","endpointAccessType":"public"}
    """.strip()  # noqa: E501
    example = example.replace('<id>', id)

    docs = """
    We take examples from:
    https://docs.primehub.io/docs/model-deployment-tutorial-prepackaged-image

    Definition example:
    """
    docs = textwrap.dedent(docs)
    explain = f'{message}\n\n{docs}{json.dumps(json.loads(example), indent=2)}'
    raise PrimeHubException(explain)


def verify_requires(config):
    # verify required fields in the config
    if not config:
        invalid_config('Deployment definition is required.')
    if 'id' not in config:
        invalid_config('id is required')
    if 'instanceType' not in config:
        invalid_config('instanceType is required')
    if 'modelImage' not in config:
        invalid_config('modelImage is required')


class Deployments(Helpful, Module):
    """
    The deployments module provides functions to manage PrimeHub Deployments

    Deployment configuration example:
    {
        "id": "<uniqe_id>",
        "name": "deploy-name",
        "modelImage": "base-notebook",
        "modelURI": "test/module/uri",
        "instanceType": "cpu-1",
        "replicas": 1
    }
    """

    @cmd(name='list', description='List deployments')
    def list(self):
        """
        List all deployments information in the current group

        :rtype list
        :return The list of deployments
        """
        query = """
        query($where: PhDeploymentWhereInput) {
          phDeployments(where: $where) {
            id
            name
            modelImage
            imagePullSecret
            description
            replicas
            stop
            endpointAccessType
            endpointClients {
              name
            }
            status
            endpoint
            replicas
            availableReplicas
            message
            pods {
              name
            }
          }
        }
        """
        results = self.request({'where': {'groupId_in': [self.group_id]}}, query)
        return results['data']['phDeployments']

    @cmd(name='get', description='Get a deployment by id', return_required=True)
    def get(self, id):
        """
        Get detail information of a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail information of a deployment
        """
        query = """
        query ($where: PhDeploymentWhereUniqueInput!) {
          phDeployment (where: $where) {
            id
            name
            modelImage
            imagePullSecret
            description
            replicas
            stop
            endpointAccessType
            endpointClients {
              name
            }
            status
            endpoint
            replicas
            availableReplicas
            message
            pods {
              name
            }
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['phDeployment']

    @cmd(name='get-history', description='Get history of a deployment by id')
    def get_history(self, id):
        """
        Get history of a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The history of a deployment
        """
        query = """
        query ($where: PhDeploymentWhereUniqueInput!) {
          phDeployment (where: $where) {
            history {
              time
              deployment {
                id
                name
                modelImage
                imagePullSecret
                description
                replicas
                stop
                endpointAccessType
                endpointClients {
                  name
                }
                status
                endpoint
                replicas
              }
            }
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['phDeployment']['history']

    @cmd(name='create', description='Create a deployment', optionals=[('file', file_flag)])
    def _create_cmd(self, **kwargs):
        """
        Create a deployment from commands

        :type file: str
        :param file: The file path of deployment configurations

        :rtype dict
        :return The detail information of the created deployment
        """
        config = primehub_load_config(filename=kwargs.get('file', None))
        return self.create(config)

    def create(self, config):
        """
        Create a deployments with config

        :type config: dict
        :param config: The deployment config

        :rtype dict
        :return The detail information of the created deployment
        """
        query = """
        mutation ($data: PhDeploymentCreateInput!) {
          createPhDeployment(data: $data) {
            id
            name
            modelImage
            imagePullSecret
            description
            replicas
            stop
            endpointAccessType
            endpointClients {
              name
            }
            status
            endpoint
            replicas
            availableReplicas
            message
            pods {
              name
            }
          }
        }
        """

        verify_requires(config)
        config['groupId'] = self.group_id
        self.verify_dependency(config)
        results = self.request({'data': config}, query)
        return results['data']['createPhDeployment']

    def verify_dependency(self, config):
        if 'instanceType' in config:
            self.primehub.instancetypes.get(config['instanceType'])

    @cmd(name='update', description='Update a deployment by id', optionals=[('file', file_flag)])
    def _update_cmd(self, id, **kwargs):
        """
        Update a deployment from commands

        :type file: str
        :param file: The file path of deployment configurations

        :rtype dict
        :return The detail information of the updated deployment
        """
        config = primehub_load_config(filename=kwargs.get('file', None))
        return self.update(id, config)

    def update(self, id, config):
        """
        Update a deployment with config

        :type id: str
        :param id: The deployment id

        :type config: dict
        :param config: The deployment config

        :rtype dict
        :return The detail information of the updated deployment
        """
        query = """
        mutation ($data: PhDeploymentUpdateInput!, $where: PhDeploymentWhereUniqueInput!) {
          updatePhDeployment(data: $data, where: $where) {
            id
            name
            modelImage
            imagePullSecret
            description
            replicas
            stop
            endpointAccessType
            endpointClients {
              name
            }
            status
            endpoint
            replicas
            availableReplicas
            message
            pods {
              name
            }
          }
        }
        """
        if not config:
            invalid_config('Deployment definition is required.')
        self.verify_dependency(config)
        results = self.request({'data': config, 'where': {'id': id}}, query, _error_handler)
        return results['data']['updatePhDeployment']

    @cmd(name='start', description='Start a deployment by id')
    def start(self, id):
        """
        Start a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail information of the started deployment
        """
        query = """
        mutation ($where:PhDeploymentWhereUniqueInput!) {
          deployPhDeployment (where: $where) {
            id
            name
            modelImage
            imagePullSecret
            description
            replicas
            stop
            endpointAccessType
            endpointClients {
              name
            }
            status
            endpoint
            replicas
            availableReplicas
            message
            pods {
              name
            }
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['deployPhDeployment']

    @cmd(name='stop', description='Stop a deployment by id')
    def stop(self, id):
        """
        Stop a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail information of the stopped deployment
        """
        query = """
        mutation ($where:PhDeploymentWhereUniqueInput!) {
          stopPhDeployment (where: $where) {
            id
            name
            modelImage
            imagePullSecret
            description
            replicas
            stop
            endpointAccessType
            endpointClients {
              name
            }
            status
            endpoint
            replicas
            availableReplicas
            message
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['stopPhDeployment']

    @ask_for_permission
    @cmd(name='delete', description='Delete a deployment by id')
    def delete(self, id, **kwargs):
        """
        Delete a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail information of the deleted deployment
        """
        query = """
        mutation ($where: PhDeploymentWhereUniqueInput!) {
          deletePhDeployment(where: $where) {
            id
          }
        }
        """
        results = self.request({'where': {'id': id}}, query, _error_handler)
        return results['data']['deletePhDeployment']

    # TODO: handle invalid pod
    @cmd(name='logs', description='Get deployment logs by id',
         optionals=[('pod', str), ('follow', toggle_flag), ('tail', int)])
    def logs(self, id, **kwargs) -> Iterator[bytes]:
        """
        Get logs of a deployment

        :type id: str
        :param id: The job id

        :type pod: str
        :param pod: The target pod to log

        :type follow: bool
        :param follow: Wait for additional logs to be appended

        :type tail: int
        :param tail: Show last n lines

        :rtype str
        :return The deployment logs
        """
        query = """
        query ($where: PhDeploymentWhereUniqueInput!) {
          phDeployment (where: $where) {
            pods {
              name
              phase
              logEndpoint
            }
          }
        }
        """

        pod_name = kwargs.get('pod', 'deploy-' + id)
        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        results = self.primehub.request({'where': {'id': id}}, query, _error_handler)
        pods = results['data']['phDeployment']['pods']
        endpoints = [p['logEndpoint'] for p in pods if p['name'].startswith(pod_name)]
        return self.primehub.request_logs(endpoints[0], follow, tail)

    @cmd(name='wait', description='Wait a deployment to complete', optionals=[('timeout', int)])
    def wait(self, id, **kwargs):
        """
        Wait a deployment in a stable state {Deployed, Stopped} or until timeout

        :type id: str
        :param id: The job id

        :type timeout: int
        :param timeout: The timeout in second

        :rtype dict
        :return The detail information of the deployment
        """
        query = """
        query ($where: PhDeploymentWhereUniqueInput!) {
          phDeployment (where: $where) {
            stop
            status
          }
        }
        """
        timeout = kwargs.get('timeout', 0)
        start_time = time.time()
        while True:
            results = self.request({'where': {'id': id}}, query, _error_handler)
            status = results['data']['phDeployment']['status']
            stop = results['data']['phDeployment']['stop']
            if (not stop and status == 'Deployed') or (stop and status == 'Stopped'):
                break
            time.sleep(1)
            if timeout != 0 and (time.time() - start_time >= timeout):
                break
        return self.get(id)

    def help_description(self):
        return "Get a deployment or list deployments"
