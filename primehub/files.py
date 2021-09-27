from primehub import Helpful, cmd, Module
from urllib.parse import urlparse
import os

from primehub.utils.optionals import toggle_flag
from primehub.utils import create_logger, SharedFileException

logger = create_logger('cmd-files')


def invalid(message):
    raise SharedFileException(message)


def _normalize_dest_path(path):
    if path is None:
        raise ValueError('path is required')

    # case empty string => .
    if path == '':
        return '.'

    # simple normalized the typo to .
    if path in ['.', './']:
        return '.'

    # the normal case
    if path == '/':
        return '/'

    # case ./abc => /abc
    if path.startswith('./'):
        return path

    # case .abc => .abc
    if path.startswith('.'):
        return path

    return path


def _normalize_user_input_path(path):
    if path is None:
        raise ValueError('path is required')

    # case empty string => /
    if path == '':
        return '/'

    # simple normalized the typo to /
    if path in ['.', './']:
        return '/'

    # the normal case
    if path == '/':
        return '/'

    # case ./abc => /abc
    if path.startswith('./'):
        return '/' + path[2:]

    # case .abc => .abc
    if path.startswith('.'):
        return path

    # case abc => /abc
    if not path.startswith('/'):
        return '/' + path

    return path


class Files(Helpful, Module):
    """
    The files module provides functions to manage Primehub Shared Files
    """

    @cmd(name='list', description='List shared files')
    def list(self, path):
        """
        The cmd to list all files and folders in the path

        :type path: str
        :param path: The path to list

        :rtype dict
        :return The detail information of files in the path
        """

        items = self._execute_list(path, limit=1)
        if items:  # directory
            return self._execute_list(path)

        items = self._execute_list(path, recursive=True, limit=1)
        if not items or items[0]['name']:
            invalid(f'No such file or directory: {path}')
            return []

        # file
        if not os.path.basename(path):  # trailing slash
            invalid(f'Not a directory: {path}')
            return []

        items[0]['name'] = os.path.basename(path)
        return items

    def _execute_list(self, path, **kwargs):
        """
        List all files and folders in the path

        :type path: str
        :param path: The path to list

        :type recursive: bool
        :param recursive: List recursively, it works when a path is a directory.

        :type limit: int
        :param limit: The maximum size of the list

        :rtype dict
        :return The detail information of files in the path
        """
        query = """
        query files($where: StoreFileWhereInput!, , $options: StoreFileListOptionInput) {
          files (where: $where, options: $options) {
            phfsPrefix
            items {
              name
              size
              lastModified
            }
          }
        }
        """
        path = _normalize_user_input_path(path)

        path_norm = os.path.normpath(path)
        recursive = kwargs.get('recursive', False)
        limit = kwargs.get('limit', 1000)
        results = self.request(
            {'where': {'phfsPrefix': path_norm, 'groupName': self.group_name},
             'options': {'recursive': recursive, 'limit': limit}},
            query)
        items = results['data']['files']['items']
        return items

    @cmd(name='download', description='Download shared files', optionals=[('recursive', toggle_flag)])
    def download(self, path, dest, **kwargs):
        """
        Download files

        :type path: str
        :param path: The path of file or folder

        :type dest: str
        :param dest: The local path to save artifacts

        :type recusive: bool
        :param recusive: Copy recursively, it works when a path is a directory.
        """

        def to_group_path(group_name: str):
            if not group_name:
                return group_name
            return group_name.replace('_', '-').lower()

        u = urlparse(self.endpoint)
        endpoint = u._replace(path=f'/api/files/groups/{to_group_path(self.group_name)}').geturl()

        # start download
        src_dst_list = self._generate_download_list(path, dest, **kwargs)
        for src, dst in src_dst_list:
            dir = os.path.dirname(dst)
            if dir and not os.path.isdir(dir):
                os.makedirs(dir)
            self.request_file(endpoint + src, dst)

    def _generate_download_list(self, path, dest, **kwargs):
        """
        Download files

        :type path: str
        :param path: The path of file or folder

        :type dest: str
        :param dest: The local path to save artifacts

        :type recusive: bool
        :param recusive: Copy recursively, it works when a path is a directory.

        :type list
        :return List of tuple of download source and destination
        """
        path = _normalize_user_input_path(path)
        recursive = kwargs.get('recursive', False)

        # check dest
        dest = _normalize_dest_path(dest)
        dest_norm = os.path.normpath(dest)
        dest_isfile = os.path.isfile(dest_norm)
        dest_dir = os.path.dirname(dest)
        if dest_dir and not os.path.isdir(dest_dir):
            invalid(f'No such file or directory: {dest_dir}')
            return []

        items = self._execute_list(path, limit=1)
        if items:  # directory
            if dest_isfile:
                invalid(f'Not a directory: {dest}')
                return []

            if not recursive:
                invalid(f'{path} is a directory, please download it recursively')
                return []

            transform = not any(os.path.basename(path))

        else:  # file or not exist
            items = self._execute_list(path, recursive=True, limit=1)
            if not items or items[0]['name']:
                invalid(f'No such file or directory: {path}')
                return []

            if not os.path.basename(path):  # trailing slash
                invalid(f'Not a directory: {path}')
                return []

            transform = not os.path.isdir(dest)

        src_dst_list = []
        path_norm = os.path.normpath(path)
        prefix = path_norm if transform else os.path.dirname(path_norm)
        prefix_len = len(os.path.join(prefix, ''))

        files_phfs = [path_norm + f['name'] for f in self._execute_list(path_norm, recursive=True)]
        for src in files_phfs:
            dst = os.path.normpath(os.path.join(dest_norm, src[prefix_len:]))
            if os.path.isdir(dst):
                logger.warning(f'cannot overwrite directory {dst} with non-directory {src}')
                continue

            is_file = False
            sub_dst = dest_norm
            dirs = src[prefix_len:].split('/')
            for dir in dirs[:-1]:
                sub_dst = os.path.join(sub_dst, dir)
                if os.path.isfile(sub_dst):
                    is_file = True
                    break
                if not os.path.exists(sub_dst):
                    break
            if is_file:
                logger.warning(f'{dest} Not a directory')
                continue

            src_dst_list.append((src, dst))

        return src_dst_list

    def help_description(self):
        return "List and download shared files"
