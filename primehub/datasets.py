from typing import Optional

from primehub import Helpful, cmd, Module
from primehub.resource_operations import GroupResourceOperation


class Datasets(Helpful, Module, GroupResourceOperation):
    """
    List datasets or get a dataset entry from the list
    """
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
    def list(self) -> list:
        """
        List datasets

        :rtype: list
        :returns: all datasets in the current group
        """
        return self.do_list(Datasets.query, Datasets.resource_name)

    @cmd(name='get', description='Get a dataset by name', return_required=True)
    def get(self, name) -> Optional[dict]:
        """
        Get a dataset from the current group

        :type name: str
        :param name: the name of a dataset

        :rtype: Optional[dict]
        :returns: a dataset
        """
        return self.do_get(Datasets.query, Datasets.resource_name, name)

    def help_description(self):
        return "Get a dataset or list datasets"
