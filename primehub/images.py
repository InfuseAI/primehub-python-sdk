from primehub import Helpful, cmd, Module, NoSuchGroup
from primehub.resource_operations import GroupResourceOperation


class Images(Helpful, Module, GroupResourceOperation):
    resource_name = 'images'
    query = """
    {
      me {
        effectiveGroups {
          name
          images {
            id
            name
            displayName
            description
            useImagePullSecret
            spec
          }
        }
      }
    }
    """

    @cmd(name='list', description='List images')
    def list(self):
        return self.do_list(Images.query, Images.resource_name)

    @cmd(name='get', description='Get image by name')
    def get(self, image_name):
        return self.do_get(Images.query, Images.resource_name, image_name)

    def help_description(self):
        return "Get a image or list images"
