from typing import Iterator

from primehub import Helpful, cmd, Module, has_data_from_stdin
from primehub.utils.permission import ask_for_permission
import time
import os
import json
import sys


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

    @cmd(name='list', description='List deployments', optionals=[('page', int)])
    def list(self, **kwargs):
        """
        List all deployments information in the current group

        :type page: int
        :param page: The page number as you can see in PrimeHub Deployments UI

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
          }
        }
        """
        results = self.request({'where': {'groupId_in': [self.group_id]}}, query)
        return results['data']['phDeployments']

    @cmd(name='get', description='Get a deployment by id')
    def get(self, id):
        """
        Get detail information of a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail infromation of a deployment
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
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
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
        results = self.request({'where': {'id': id}}, query)
        return results['data']['phDeployment']['history']

    # TODO: add -f
    # TODO: handel invalid config
    @cmd(name='create', description='Create a deployment', optionals=[('file', str)])
    def create_cmd(self, **kwargs):
        """
        Create a deployment from commands

        :type file: str
        :param file: The file path of deployment configurations

        :rtype dict
        :return The detail infromation of the created deployment
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
        Create a deployments with config

        :type config: dict
        :param config: The deployment config

        :rtype dict
        :return The detail infromation of the created deployment
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
          }
        }
        """
        config['groupId'] = self.group_id
        results = self.request({'data': config}, query)
        return results['data']['createPhDeployment']

    # TODO: add -f
    # TODO: handel invalid config
    @cmd(name='update', description='Update a deployment by id', optionals=[('file', str)])
    def update_cmd(self, id, **kwargs):
        """
        Update a deployment from commands

        :type file: str
        :param file: The file path of deployment configurations

        :rtype dict
        :return The detail infromation of the updated deployment
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
        Update a deployment with config

        :type id: str
        :param id: The deployment id

        :type config: dict
        :param config: The deployment config

        :rtype dict
        :return The detail infromation of the updated deployment
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
          }
        }
        """
        results = self.request({'data': config, 'where': {'id': id}}, query)
        return results['data']['updatePhDeployment']

    @cmd(name='start', description='Start a deployment by id')
    def start(self, id):
        """
        Start a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail infromation of the started deployment
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
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        return results['data']['deployPhDeployment']

    @cmd(name='stop', description='Stop a deployment by id')
    def stop(self, id):
        """
        Stop a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail infromation of the stopped deployment
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
        results = self.request({'where': {'id': id}}, query)
        return results['data']['stopPhDeployment']

    @ask_for_permission
    @cmd(name='delete', description='Delete a deployment by id')
    def delete(self, id, **kwargs):
        """
        Delete a deployment by id

        :type id: str
        :param id: The deployment id

        :rtype dict
        :return The detail infromation of the deleted deployment
        """
        query = """
        mutation ($where: PhDeploymentWhereUniqueInput!) {
          deletePhDeployment(where: $where) {
            id
          }
        }
        """
        results = self.request({'where': {'id': id}}, query)
        return results['data']['deletePhDeployment']

    # TODO: handle invalid pod
    # TODO: allow fuzzy pod name
    @cmd(name='logs', description='Get deployment logs by id',
         optionals=[('pod', str), ('follow', bool), ('tail', int)])
    def logs(self, id, **kwargs) -> Iterator[str]:
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

        pod = kwargs.get('pod', '')
        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        results = self.primehub.request({'where': {'id': id}}, query)
        endpoints = [p['logEndpoint'] for p in results['data']['phDeployment']['pods'] if p['name'] == pod]
        endpoint = endpoints[0]
        return self.primehub.request_logs(endpoint, follow, tail)

    @cmd(name='wait', description='Wait a deployment to complete', optionals=[('timeout', int)])
    def wait(self, id, **kwargs):
        """
        Wait a deployment in a stable state {Deployed, Stopped} or until timeout

        :type id: str
        :param id: The job id

        :type timeout: int
        :param timeout: The timeout in second

        :rtype dict
        :return The detail infromation of the deployment
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
            results = self.request({'where': {'id': id}}, query)
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
