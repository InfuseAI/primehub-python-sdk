import textwrap
from typing import Iterator, Any, Optional

from primehub import Helpful, cmd, Module
from primehub.utils.display import display_tree_like_format


def timestamp_to_isoformat(timestamp):
    unix_timestamp = int(int(timestamp) / 1000)
    from datetime import datetime
    return datetime.fromtimestamp(unix_timestamp)


class Models(Helpful, Module):

    @cmd(name='list', description='List models', return_required=True)
    def list(self) -> Iterator:
        """
        List models

        :rtype: Iterator
        :returns: All registered models
        """

        query = """
        query QueryModels($group: String!) {
          mlflow(where: { group: $group }) {
            ...MLflowSettingInfo
          }
          models(where: { group: $group }) {
            ...ModelInfo
          }
        }
        fragment MLflowSettingInfo on MLflowSetting {
          trackingUri
          uiUrl
        }
        fragment ModelInfo on Model {
          name
          creationTimestamp
          lastUpdatedTimestamp
          description
          latestVersions {
            name
            version
          }
        }
        """

        results = self.request({'group': self.group_name}, query)
        if 'data' in results:
            results = results['data']
            for m in results['models']:
                m['creationTimestamp'] = timestamp_to_isoformat(m['creationTimestamp'])
                m['lastUpdatedTimestamp'] = timestamp_to_isoformat(m['lastUpdatedTimestamp'])
                versions = m.pop('latestVersions')
                if len(versions):
                    m['latestVersion'] = versions[0]['version']
                yield m
        return results

    @cmd(name='get', description='Get the model', return_required=True)
    def get(self, name: str) -> dict:
        """
        Get the model

        :type name: str
        :param name: The model name

        :rtype: dict
        :return: The detail information of a model
        """

        query = """
        query QueryModel($group: String!, $name: String!) {
          mlflow(where: { group: $group }) {
            ...MLflowSettingInfo
          }
          model(where: { group: $group, name: $name }) {
            ...ModelInfo
          }
          modelVersions(where: { group: $group, name: $name }) {
            ...ModelVersionInfo
          }
        }
        fragment MLflowSettingInfo on MLflowSetting {
          trackingUri
          uiUrl
        }
        fragment ModelInfo on Model {
          name
          creationTimestamp
          lastUpdatedTimestamp
          description
          latestVersions {
            name
            version
          }
        }
        fragment ModelVersionInfo on ModelVersion {
          name
          version
          creationTimestamp
          lastUpdatedTimestamp
          deployedBy
        }
        """

        results = self.request({'group': self.group_name, 'name': name}, query)
        if 'data' not in results:
            return results
        results = results['data']
        return results

    @cmd(name='list-versions', description='List versions of the model', return_required=True)
    def list_versions(self, model: str) -> Iterator:
        """
        List versions of the model

        :type model: str
        :param model: The model name

        :rtype: Iterator
        :returns: All versions of a model
        """

        query = """
        query QueryModel($group: String!, $name: String!) {
          modelVersions(where: { group: $group, name: $name }) {
            ...ModelVersionInfo
          }
        }
        fragment ModelVersionInfo on ModelVersion {
          name
          version
          creationTimestamp
          lastUpdatedTimestamp
          source
          deployedBy
        }
        """

        results = self.request({'group': self.group_name, 'name': model}, query)
        if 'data' not in results:
            return results
        results = results['data']
        for m in results['modelVersions']:
            m['creationTimestamp'] = timestamp_to_isoformat(m['creationTimestamp'])
            m['lastUpdatedTimestamp'] = timestamp_to_isoformat(m['lastUpdatedTimestamp'])
            yield m
        return results

    @cmd(name='get-version', description='Get a version of the model', return_required=True)
    def get_version(self, model: str, version: str) -> dict:
        """
        Get a version of the model

        :type model: str
        :param model: The model name

        :type version: str
        :param version: Verson number

        :rtype: dict
        :return: The detail information of a model version
        """

        query = """
        query QueryModelVersion($group: String!, $name: String!, $version: String!) {
          mlflow(where: { group: $group }) {
            ...MLflowSettingInfo
          }
          modelVersion(where: { group: $group, name: $name, version: $version }) {
            ...ModelVersionInfo
            run
          }
        }
        fragment MLflowSettingInfo on MLflowSetting {
          trackingUri
          uiUrl
        }
        fragment ModelVersionInfo on ModelVersion {
          name
          version
          creationTimestamp
          lastUpdatedTimestamp
          source
          deployedBy
        }
        """

        results = self.request({'group': self.group_name, 'name': model, 'version': version}, query)
        if 'data' not in results:
            return results
        results = results['data']['modelVersion']
        return results

    @cmd(name='list-runs', description='List runs of an experiment', return_required=True)
    def list_runs(self, experiment_name: str):
        """
        List runs of an experiment

        :type experiment_name: str
        :param experiment_name: The experiment name

        :rtype: list
        :return: The runs of an experiment
        """

        query = """
        query MLflowRuns($where: MLflowExperimentWhereUniqueInput!) {
          mlflowRuns(where: $where)
        }
        """
        where = {
            'experimentName': experiment_name,
            'group': self.group_name,
        }

        results = self.request({'where': where}, query)
        if 'data' in results:
            results = results['data']
            for r in results['mlflowRuns']:
                m = {
                    'runId': r['info']['runId'],
                    'experimentId': r['info']['experimentId'],
                    'status': r['info']['status'],
                    'startTime': timestamp_to_isoformat(r['info']['startTime']),
                }
                if r['info'].get('endTime'):
                    m['endTime'] = timestamp_to_isoformat(r['info']['endTime'])
                yield m
        return results

    @cmd(name='list-artifacts', description='List artifacts of a run', return_required=True, optionals=[('path', str)])
    def _list_artifacts(self, run_id: str, **kwargs):
        """
        List artifacts of a run

        :type run_id: str
        :param run_id: The run id

        :type path: str
        :param path: Add `--path <path>` to filter artifacts matching this path

        :rtype: list
        :return: The artifacts of a run
        """
        path = kwargs.get('path')
        return self.list_artifacts(run_id, path)

    def list_artifacts(self, run_id: str, path: Optional[str] = None):
        """
        List artifacts of a run

        :type run_id: str
        :param run_id: The run id

        :type path: str
        :param path: Filter artifacts matching this path, defaults to None

        :rtype: list
        :return: The artifacts of a run
        """

        query = """
        query MLflowArtifact($where: MLflowRunWhereUniqueInput!) {
          mlflowArtifact(where: $where)
        }
        """
        where = {
            'runId': run_id,
            'group': self.group_name,
        }
        if path:
            where['path'] = path

        results = self.request({'where': where}, query)
        if 'data' not in results:
            return results
        if 'files' in results['data']['mlflowArtifact']:
            return results['data']['mlflowArtifact']['files']
        return []

    @cmd(name='register', description='Register a model')
    def register(self, name: str, run_id: str, path: str):
        """
        Register a model

        :type name: str
        :param name: Model name

        :type run_id: str
        :param run_id: The run id

        :type path: str
        :param path: The location of the model artifacts
        """

        query = """
        mutation RegisterModel($where: ModelRegisterInput!) {
          registerModel(where: $where)
        }
        """
        where = {
            'name': name,
            'runId': run_id,
            'path': path,
            'group': self.group_name,
        }

        results = self.request({'where': where}, query)
        if 'data' not in results:
            return results
        return results['data']['registerModel']

    @cmd(name='deploy', description='Deploy the model version to the speific deployment', return_required=True)
    def deploy(self, model: str, version: str, deploy_id: str) -> dict:
        """
        Deploy the model version to the speific deployment

        :type model: str
        :param model: The model name

        :type version: str
        :param version: Verson number

        :type deploy_id: str
        :param deploy_id: Deployment id

        :rtype: dict
        :return: The detail information of the updated deployment
        """

        return self.primehub.deployments.update(deploy_id, {'modelURI': f'models:/{model}/{version}'})

    def help_description(self):
        return "Manage models"

    def display(self, action: dict, value: Any):
        from io import StringIO

        if action['func'] == 'get' and self.get_display().name != 'json':
            value['model']['creationTimestamp'] = timestamp_to_isoformat(value['model']['creationTimestamp'])
            value['model']['lastUpdatedTimestamp'] = timestamp_to_isoformat(value['model']['lastUpdatedTimestamp'])

            versions = value.pop('modelVersions')
            self.get_display().display(action, value, self.primehub.stdout)
            self.get_display().display(action, "versions:", self.primehub.stdout)
            for version in versions:
                version['creationTimestamp'] = timestamp_to_isoformat(version['creationTimestamp'])
                version['lastUpdatedTimestamp'] = timestamp_to_isoformat(version['lastUpdatedTimestamp'])

                self.get_display().display(action, "  -", self.primehub.stdout)
                display_tree_like_format(version, self.primehub.stdout, 0, 2)

        elif action['func'] == 'get_version' and self.get_display().name != 'json':
            version = value
            version['creationTimestamp'] = timestamp_to_isoformat(version['creationTimestamp'])
            version['lastUpdatedTimestamp'] = timestamp_to_isoformat(version['lastUpdatedTimestamp'])

            run = value.pop('run')
            run['info']['startTime'] = timestamp_to_isoformat(run['info']['startTime'])
            run['info']['endTime'] = timestamp_to_isoformat(run['info']['endTime'])

            data = run.pop('data')
            self.get_display().display(action, version, self.primehub.stdout)
            self.get_display().display(action, "run:", self.primehub.stdout)
            display_tree_like_format(run, self.primehub.stdout, 0, 2)
            self.get_display().display(action, "  data:", self.primehub.stdout)

            # print metrics table
            for metric in data['metrics']:
                metric['timestamp'] = timestamp_to_isoformat(metric['timestamp'])
            self.get_display().display(action, "    metrics:", self.primehub.stdout)
            metrics_io = StringIO()
            self.get_display().display(action, data['metrics'], metrics_io)
            self.get_display().display(action,
                                       textwrap.indent(metrics_io.getvalue().strip(), ' ' * 6),
                                       self.primehub.stdout)

            # print params table
            self.get_display().display(action, "    params:", self.primehub.stdout)
            s = StringIO()
            self.get_display().display(action, data['params'], s)
            self.get_display().display(action,
                                       textwrap.indent(s.getvalue().strip(), ' ' * 6),
                                       self.primehub.stdout)

        else:
            super(Models, self).display(action, value)
