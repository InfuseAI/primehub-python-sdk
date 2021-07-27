from primehub import Helpful, cmd, Module
from primehub.resource_operations import GroupResourceOperation


class InstanceTypes(Helpful, Module, GroupResourceOperation):
    resource_name = 'instanceTypes'
    query = """
    query {
      me {
        effectiveGroups {
          name
          instanceTypes {
            id
            name
            displayName
            description
          }
        }
      }
    }
    """

    @cmd(name='list', description='List instance types')
    def list(self):
        return self.do_list(InstanceTypes.query, InstanceTypes.resource_name)

    @cmd(name='get', description='Get an instance type by name')
    def get(self, name):
        return self.do_get(InstanceTypes.query, InstanceTypes.resource_name, name)

    def help_description(self):
        return "Get an instance types of list instance types"
