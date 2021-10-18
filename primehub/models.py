from typing import Iterator

from primehub import Helpful, cmd, Module


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

    @cmd(name='get-version', description='Get a version of the model', return_required=True)
    def get_version(self, model: str, version: str) -> dict:
        return {}

    def help_description(self):
        return "Manage models"
