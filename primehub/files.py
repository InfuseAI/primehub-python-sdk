from primehub import Helpful, cmd, Module
from urllib.parse import urlparse
import os
import sys

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

    @cmd(name='get-phfs-uri', description='Get PHFS URI')
    def get_phfs_uri(self, path):
        """
        The cmd to convert path in PHFS to the PHFS URI

        :type path: str
        :param path: The path

        :rtype str
        :return The PHFS URI
        """
        path_norm = _normalize_user_input_path(path)
        path_norm = os.path.normpath(path_norm)

        items = self._execute_list(path_norm, limit=0)
        if items:
            return f"phfs://{path_norm}"
        else:
            raise SharedFileException(f"PHFS path not found: {path}")

    @cmd(name='list', description='List shared files')
    def list(self, path):
        """
        The cmd to list all files and folders in the path

        :type path: str
        :param path: The path to list

        :rtype dict
        :return The detail information of files in the path
        """

        path_norm = _normalize_user_input_path(path)
        path_norm = os.path.normpath(path_norm)

        items = self._execute_list(path_norm, limit=1)
        if items:  # directory
            return self._execute_list(path_norm)

        items = self._execute_list(path_norm, recursive=True, limit=1)
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
        query files($where: StoreFileWhereInput!, $options: StoreFileListOptionInput) {
          files(where: $where, options: $options) {
            phfsPrefix
            items {
              name
              size
              lastModified
            }
          }
        }
        """
        recursive = kwargs.get('recursive', False)
        limit = kwargs.get('limit', 1000)
        results = self.request(
            {'where': {'phfsPrefix': path, 'groupName': self.group_name},
             'options': {'recursive': recursive, 'limit': limit}},
            query)
        items = results['data']['files']['items']

        # patch PHFS-URI
        for x in items:
            if path == '/':
                x['phfsUri'] = f"phfs:///{x['name']}"
            else:
                x['phfsUri'] = f"phfs://{path}/{x['name']}"
        return items

    def _primehub_store_endpoint(self):
        def to_group_path(group_name: str):
            if not group_name:
                return group_name
            return group_name.replace('_', '-').lower()

        u = urlparse(self.endpoint)
        endpoint = u._replace(path=f'/api/files/groups/{to_group_path(self.group_name)}').geturl()

        return endpoint

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

        endpoint = self._primehub_store_endpoint()
        filter_func = kwargs.get('filter_func', None)

        # start download
        src_dst_list = self._generate_download_list(path, dest, **kwargs)
        for src, dst in src_dst_list:
            if filter_func and filter_func(src):
                self._warning_skip(src)
                continue
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
        path_norm = os.path.normpath(path)
        path_isprefix = path.endswith('/')
        recursive = kwargs.get('recursive', False)
        download_single_file = False

        # check dest
        dest = _normalize_dest_path(dest)
        dest_norm = os.path.normpath(dest)
        dest_isfile = os.path.isfile(dest_norm)
        dest_dir = os.path.dirname(dest)
        if dest_dir and not os.path.isdir(dest_dir):
            invalid(f'No such file or directory: {dest_dir}')
            return []

        if not path_isprefix and not recursive:
            # to download a file
            items = self._execute_list(path_norm, recursive=True, limit=1)
            if not items or items[0]['name']:
                invalid(f'No such file: {path}')

            download_single_file = True
        else:
            # to download directory
            items = self._execute_list(path_norm, limit=1)
            if items:
                if dest_isfile:
                    invalid(f'Not a directory: {dest}')
                    return []

                if not recursive:
                    invalid(f'{path} is a directory, please download it recursively')
                    return []

            else:  # directory not exist
                items = self._execute_list(path_norm, recursive=True, limit=1)
                if not items or items[0]['name']:
                    invalid(f'No such file or directory: {path}')
                    return []

                if not os.path.basename(path):  # trailing slash
                    invalid(f'Not a directory: {path}')
                    return []

                download_single_file = True

        src_dst_list = []
        prefix = os.path.dirname(path_norm)
        prefix_len = len(os.path.join(prefix, ''))

        if download_single_file:
            files_phfs = [path_norm]
            if not os.path.isdir(dest):
                prefix_len = len(os.path.join(path_norm, ''))
        else:
            if not path_norm.endswith('/'):
                path_norm += '/'
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

    @cmd(name='upload', description='Upload shared files', optionals=[('recursive', toggle_flag)])
    def upload(self, src, path, **kwargs):
        """
        Upload files

        :type path: str
        :param path: The path of file or folder

        :type src: str
        :param src: The local path to save artifacts

        :type recusive: bool
        :param recusive: Upload recursively, it works when a src is a directory.
        """
        path = _normalize_user_input_path(path)
        recursive = kwargs.get('recursive', False)
        filter_func = kwargs.get('filter_func', None)

        # check src
        if not os.path.exists(src):
            invalid(f'No such file or directory: {src}')
            return []

        file_paths = []
        if recursive is True:
            if os.path.isfile(src):
                file_paths.append(os.path.abspath(src))
            else:
                for (dirpath, dirnames, filenames) in os.walk(src):
                    for filename in filenames:
                        file_paths.append(os.path.join(dirpath, filename))
            pass
        else:
            if os.path.isfile(src):
                filename = os.path.abspath(src)
                file_paths.append(filename)
            else:
                invalid(f'{src} is not a file')
                return []
            pass

        endpoint = self._primehub_store_endpoint()
        result = []
        for filepath in file_paths:
            try:
                phfs_path = path
                if os.path.isfile(src):
                    if not recursive and not path.endswith('/'):
                        # overwrite a phfs object
                        phfs_path = path
                    else:
                        phfs_path = os.path.join(path, os.path.basename(src))
                else:
                    phfs_path = os.path.join(path, os.path.relpath(filepath, os.path.dirname(src)))
                    pass
                if filter_func and filter_func(phfs_path):
                    self._warning_skip(phfs_path)
                    continue
                print(f'[Uploading] {filepath} -> phfs://{phfs_path}', file=self.primehub.stderr)
                response = self._execute_upload(endpoint, filepath, phfs_path)
                response['phfs'] = phfs_path
                response['file'] = filepath
                result.append(response)
            except Exception as e:
                print(e, file=sys.stderr)
                result.append({
                    'success': False,
                    'message': e
                })
        return result

    def _warning_skip(self, path):
        logger.warning(f'[Warning] skip path: {path}')

    def _execute_upload(self, endpoint, src, path):
        return self.upload_file(endpoint + path, src)

    @cmd(name='delete', description='delete shared files', optionals=[('recursive', toggle_flag)])
    def delete(self, path, **kwargs):
        """
        Delete files

        :type path: str
        :param path: The path of file or folder

        :type recursive: bool
        :param recursive: Delete recursively, it works when a path is a directory.
        """

        query = """
        mutation deleteFiles(
          $where: StoreFileWhereInput!
          $options: StoreFileDeleteOptionInput
        ) {
          deleteFiles(where: $where, options: $options)
        }
        """
        recursive = kwargs.get('recursive', False)
        phfs_prefix = self._generate_prefix(path, recursive)

        variables = {'options': {'recursive': recursive},
                     'where': {'phfsPrefix': phfs_prefix, 'groupName': self.group_name}}

        result = self.request(variables, query)
        if 'data' in result:
            return result['data']
        return result

    def _generate_prefix(self, path, recursive) -> str:
        path = _normalize_user_input_path(path)
        path_norm = os.path.normpath(path)
        path_isprefix = path.endswith('/')
        delete_single_file = False

        if not path_isprefix and not recursive:
            # to delete a file
            items = self._execute_list(path_norm, recursive=True, limit=1)
            if not items or items[0]['name']:
                invalid(f'No such file: {path}')

            delete_single_file = True
        else:
            items = self._execute_list(path_norm, limit=1)
            if items:  # directory
                if not recursive:
                    invalid(f'{path} is a directory, please delete it recursively')

            else:  # file or not exist
                items = self._execute_list(path_norm, recursive=True, limit=1)
                if not items or items[0]['name']:
                    invalid(f'No such file or directory: {path}')

                if not os.path.basename(path):  # trailing slash
                    invalid(f'Not a directory: {path}')

                delete_single_file = True

        if path_norm == '/':
            # delete from root
            return ''

        if path_norm.startswith('/'):
            path_norm = path_norm[1:]

        if delete_single_file:
            return path_norm

        # prevent from deleting objects with the same prefix, e.g., /config, /config2
        return path_norm + '/'

    def help_description(self):
        return "List and download shared files"
