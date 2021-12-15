from typing import Optional

from primehub import Helpful, cmd, Module


class Secrets(Helpful, Module):
    """
    Query secrets for Image Pull Secrets
    """

    @cmd(name='list', description='List secrets')
    def list(self) -> list:
        """
        List secrets

        :rtype: list
        :returns: secrets
        """
        query = """
        {
          secrets(where: { ifDockerConfigJson: true }) {
            id
            name
            type
          }
        }
        """
        results = self.request({}, query)
        return results['data']['secrets']

    @cmd(name='get', description='Get a secret by id', return_required=True)
    def get(self, id: str) -> Optional[dict]:
        """
        Get the secret by id

        :type id: str
        :param id: the id of a secret

        :rtype: Optional[dict]
        :returns: a secret
        """
        secret = self.list()
        s = [x for x in secret if x['id'] == id]
        if s:
            return s[0]
        return None

    def help_description(self):
        return "Get a secret or list secrets"
