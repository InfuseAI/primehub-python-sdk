from primehub import Helpful, cmd, Module
from urllib.parse import urlparse
import os


class Files(Helpful, Module):

    @cmd(name='list', description='List shared files')
    def list(self, path):
        query = """
        query files($where: StoreFileWhereInput!) {
          files (where: $where) {
            prefix
            phfsPrefix
            items {
              name
              size
              lastModified
            }
          }
        }
        """
        results = self.request({'where': {'phfsPrefix': path, 'groupName': 'phusers'}}, query)
        return results['data']['files']['items']

    # TODO: handel path or dest does not exist
    @cmd(name='download', description='Download shared files', optionals=[('recursive', bool)])
    def download(self, path, dest, **kwargs):
        u = urlparse(self.primehub_config.endpoint)
        endpoint = u._replace(path='/api/files/groups/' + self.primehub_config.group_info['name']).geturl()

        if dest[-1] != '/':
            dest = dest + '/'

        if kwargs.get('recursive', False):
            if path[-1] != '/':     # avoid files and directories with the same prefix
                path = path + '/'
            dirname = os.path.dirname(path[:-1])
            dirs = [path]
            while dirs:
                print(dirs)
                sub_dirs = []
                for dir in dirs:
                    for file in self.list(dir):
                        p = dir + file['name']
                        if p[-1] == '/':   # folder
                            sub_dirs.append(p)
                        else:              # file
                            self.request_file(endpoint + path + p, dest + p[len(dirname):])
                dirs = sub_dirs
            return

        # single file
        self.request_file(endpoint + path, dest + os.path.basename(path))
        return

    def help_description(self):
        return "Get a job or list jobs"
