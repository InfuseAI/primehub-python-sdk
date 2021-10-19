import textwrap
from typing import Iterator, Any

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
          mlflow(where: {group: $group}) {
            ...MLflowSettingInfo
          }
          models(where: {group: $group}) {
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
                m['latestVersion'] = versions[0]['version']
                yield m
        return results

    @cmd(name='get', description='Get the model', return_required=True)
    def get(self, name):
        query = """
        query QueryModel($group: String!, $name: String!) {
          mlflow(where: {group: $group}) {
            ...MLflowSettingInfo
          }
          model(where: {group: $group, name: $name}) {
            ...ModelInfo
          }
          modelVersions(where: {group: $group, name: $name}) {
            ...ModelVersionInfo
            run
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

    @cmd(name='get-version', description='Get a version of the model', return_required=True)
    def get_version(self, model: str, version: str) -> dict:
        return {}

    def help_description(self):
        return "Manage models"

    def display(self, action: dict, value: Any):
        from io import StringIO

        if action['func'] == 'get' and self.get_display().name != 'json':
            model = value
            versions = value.pop('modelVersions')
            self.get_display().display(action, model, self.primehub.stdout)
            self.get_display().display(action, "models:", self.primehub.stdout)
            for versioned in versions:
                data = versioned['run'].pop('data')
                display_tree_like_format(versioned, self.primehub.stdout, 0, 2)

                # print metrics table
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
