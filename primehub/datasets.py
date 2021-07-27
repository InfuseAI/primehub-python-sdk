from primehub import Helpful, cmd, Module
from primehub.resource_operations import GroupResourceOperation


class Datasets(Helpful, Module, GroupResourceOperation):
    resource_name = 'datasets'
    query = """
    query {
      me {
        effectiveGroups {
          name
          datasets {
            id
            name
            displayName
            description
            type
          }
        }
      }
    }
    """

    @cmd(name='list', description='List datasets')
    def list(self):
        return self.do_list(Datasets.query, Datasets.resource_name)

    @cmd(name='get', description='Get a dataset by name')
    def get(self, name):
        return self.do_get(Datasets.query, Datasets.resource_name, name)

    def help_description(self):
        return "Get a dataset or list datasets"
