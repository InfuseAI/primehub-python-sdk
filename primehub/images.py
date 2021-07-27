from primehub import Helpful, cmd, Module, NoSuchGroup


class Images(Helpful, Module):

    @cmd(name='list', description='List images')
    def list(self):
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
        results = self.request({}, query)
        for g in results['data']['me']['effectiveGroups']:
            if self.primehub_config.group == g['name']:
                return g['images']
        raise NoSuchGroup(self.primehub_config.group)

    @cmd(name='get', description='Get image by name')
    def get(self, image_name):
        images = self.list()
        image = [x for x in images if x['name'] == image_name]
        if image:
            return image[0]
        return None

    def help_description(self):
        return "Get a image or list images"
