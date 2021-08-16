import os
from unittest import mock

from primehub.files import _normalize_user_input_path, _normalize_dest_path
from tests import BaseTestCase
from primehub.utils import create_logger, SharedFileException

logger = create_logger('primehub-test')

"""
Consider folloing files
PHFS:
/
├── l0.csv
└── deep/
    ├── l1.csv
    └── sub/
        ├── l2.csv
        └── path/
            └── l3.csv

Current local directroy:
./
├── sub (file)
└── l2.csv/
"""


def mock_request_side_effect(*args):
    phfs_files = ['/l0.csv', '/deep/l1.csv', '/deep/sub/l2.csv', '/deep/sub/path/l3.csv']

    prefix = args[0]['where']['phfsPrefix']
    recursive = args[0]['options']['recursive']
    limit = args[0]['options']['limit']

    filter_files = [f[len(prefix):] for f in phfs_files if f.startswith(prefix)]
    if not recursive:
        if prefix == '/':
            filter_files = [f for f in filter_files if f]
        else:
            filter_files = [f[1:] for f in filter_files if f and f[0] == '/']
        filter_files = [f if f.find('/') == -1 else f[:f.find('/') + 1] for f in filter_files]

    filter_files = list(set(filter_files))
    filter_files = filter_files[: limit]
    items = [{'name': f} for f in filter_files]
    return {'data': {'files': {'items': items}}}


def mock_walk_side_effect(name):
    if name not in ['.', './', '']:
        return []
    else:
        return [('./', ('l2.csv',), ('sub',)), ('./l2.csv', (), ())]


def mock_isfile_side_effect(name):
    return name in ['./sub', 'sub']


def mock_isdir_side_effect(name):
    return name in ['/', '.', './', './l2.csv', './l2.csv/', 'l2.csv', 'l2.csv/']


class TestCmdFiles(BaseTestCase):
    def setUp(self) -> None:
        super(TestCmdFiles, self).setUp()
        self.maxDiff = None

        self.sdk.primehub_config.endpoint = 'https://example.primehub.io/api/graphql'
        self.sdk.primehub_config.group_info = {'name': 'phusers', 'id': 'any-id'}
        self.mock_request.return_value = {
            'data': {
                'me': {
                    'effectiveGroups': [
                        {'name': 'phusers', 'foobar': [dict(name="3", value="3")]},
                    ]
                }
            }
        }

        self.mock_request.side_effect = mock_request_side_effect

    def assertFileListEqual(self, a: list, b: list):
        self.assertEqual(sorted(a), sorted(b))

    def assertDictListEqual(self, a: list, b: list):
        from operator import itemgetter
        a = sorted(a, key=itemgetter('name'))
        b = sorted(b, key=itemgetter('name'))
        self.assertEqual(a, b)

    def test_files_list(self):
        list_cmd = self.sdk.files.list

        # single file
        self.assertDictListEqual(list_cmd('/l0.csv'), [{'name': 'l0.csv'}])
        self.assertDictListEqual(list_cmd('/deep/sub/path/l3.csv'), [{'name': 'l3.csv'}])

        # directory
        self.assertDictListEqual(list_cmd('/'), [{'name': 'deep/'}, {'name': 'l0.csv'}])
        self.assertDictListEqual(list_cmd('/deep'), [{'name': 'sub/'}, {'name': 'l1.csv'}])
        self.assertDictListEqual(list_cmd('/deep/'), [{'name': 'sub/'}, {'name': 'l1.csv'}])
        self.assertDictListEqual(list_cmd('deep'), [{'name': 'sub/'}, {'name': 'l1.csv'}])

        # incomplete or non-exist path
        with self.assertRaises(SharedFileException) as e:
            self.assertDictListEqual(list_cmd('/l0'), [])
        self.assertEqual(str(e.exception), 'No such file or directory: /l0')

        with self.assertRaises(SharedFileException) as e:
            self.assertDictListEqual(list_cmd('/l0.csv/'), [])
        self.assertEqual(str(e.exception), 'Not a directory: /l0.csv/')

        with self.assertRaises(SharedFileException) as e:
            self.assertDictListEqual(list_cmd('/de'), [])
        self.assertEqual(str(e.exception), 'No such file or directory: /de')

        with self.assertRaises(SharedFileException) as e:
            self.assertDictListEqual(list_cmd('/none'), [])
        self.assertEqual(str(e.exception), 'No such file or directory: /none')

    @mock.patch('os.walk', mock.MagicMock(side_effect=mock_walk_side_effect))
    @mock.patch('os.path.isdir', mock.MagicMock(side_effect=mock_isdir_side_effect))
    @mock.patch('os.path.isfile', mock.MagicMock(side_effect=mock_isfile_side_effect))
    def test_files_get_download_src_dst_list_directory_1(self):
        get_download_src_dst_list = self.sdk.files._generate_download_list
        expected = [('/l0.csv', 'l0.csv'),
                    ('/deep/l1.csv', 'deep/l1.csv'),
                    ('/deep/sub/l2.csv', 'deep/sub/l2.csv'),
                    ('/deep/sub/path/l3.csv', 'deep/sub/path/l3.csv')]

        actual = get_download_src_dst_list('/', '.', recursive=True)
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, expected)

        # directory has to downlowd recursively
        with self.assertRaises(SharedFileException):
            actual = get_download_src_dst_list('.', '.')

    @mock.patch('os.walk', mock.MagicMock(side_effect=mock_walk_side_effect))
    @mock.patch('os.path.isdir', mock.MagicMock(side_effect=mock_isdir_side_effect))
    @mock.patch('os.path.isfile', mock.MagicMock(side_effect=mock_isfile_side_effect))
    def test_files_get_download_src_dst_list_directory_2(self):
        get_download_src_dst_list = self.sdk.files._generate_download_list

        actual = get_download_src_dst_list('/deep', '.', recursive=True)
        actual = self.norm_src_dst_list(actual)
        expected = [('/deep/l1.csv', 'deep/l1.csv'),
                    ('/deep/sub/l2.csv', 'deep/sub/l2.csv'),
                    ('/deep/sub/path/l3.csv', 'deep/sub/path/l3.csv')]
        self.assertFileListEqual(actual, expected)

        actual = get_download_src_dst_list('/deep/sub', '', recursive=True)
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [])

        with self.assertRaises(SharedFileException) as e:
            actual = get_download_src_dst_list('/deep', './sub', recursive=True)
        self.assertEqual(str(e.exception), 'Not a directory: ./sub')

        with self.assertRaises(SharedFileException) as e:
            actual = get_download_src_dst_list('/deep', 'not/exist/dir', recursive=True)
        self.assertEqual(str(e.exception), 'No such file or directory: not/exist')

        actual = get_download_src_dst_list('/deep/', '.', recursive=True)
        actual = self.norm_src_dst_list(actual)
        expected = [('/deep/l1.csv', 'l1.csv')]
        self.assertFileListEqual(actual, expected)

        actual = get_download_src_dst_list('/deep/sub/', '.', recursive=True)
        actual = self.norm_src_dst_list(actual)
        expected = [('/deep/sub/path/l3.csv', 'path/l3.csv')]
        self.assertFileListEqual(actual, expected)

        actual = get_download_src_dst_list('/deep/sub/', 'new', recursive=True)
        actual = self.norm_src_dst_list(actual)
        expected = [('/deep/sub/l2.csv', 'new/l2.csv'),
                    ('/deep/sub/path/l3.csv', 'new/path/l3.csv')]

        self.assertFileListEqual(actual, expected)
        actual = get_download_src_dst_list('/deep/sub', 'new', recursive=True)
        actual = self.norm_src_dst_list(actual)
        expected = [('/deep/sub/l2.csv', 'new/sub/l2.csv'),
                    ('/deep/sub/path/l3.csv', 'new/sub/path/l3.csv')]
        self.assertFileListEqual(actual, expected)

    @mock.patch('os.walk', mock.MagicMock(side_effect=mock_walk_side_effect))
    @mock.patch('os.path.isdir', mock.MagicMock(side_effect=mock_isdir_side_effect))
    @mock.patch('os.path.isfile', mock.MagicMock(side_effect=mock_isfile_side_effect))
    def test_files_get_download_src_dst_list_file(self):
        get_download_src_dst_list = self.sdk.files._generate_download_list
        # recursive does not effect donwload a file
        actual = get_download_src_dst_list('l0.csv', '.', recursive=True)
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [('/l0.csv', 'l0.csv')])

        actual = get_download_src_dst_list('l0.csv', '.')
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [('/l0.csv', 'l0.csv')])

        actual = get_download_src_dst_list('l0.csv', '/')
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [('/l0.csv', '/l0.csv')])

        actual = get_download_src_dst_list('l0.csv', 'sub')
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [('/l0.csv', 'sub')])

        actual = get_download_src_dst_list('l0.csv', 'l2.csv')
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [('/l0.csv', 'l2.csv/l0.csv')])

        actual = get_download_src_dst_list('l0.csv', 'l2.csv/')
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [('/l0.csv', 'l2.csv/l0.csv')])

        actual = get_download_src_dst_list('l0.csv', 'l2.csv/local.csv')
        actual = self.norm_src_dst_list(actual)
        self.assertFileListEqual(actual, [('/l0.csv', 'l2.csv/local.csv')])

        with self.assertRaises(SharedFileException) as e:
            actual = get_download_src_dst_list('l0.csv/', '.')
        self.assertEqual(str(e.exception), 'Not a directory: /l0.csv/')

        with self.assertRaises(SharedFileException) as e:
            actual = get_download_src_dst_list('l0.csv', 'not_exist/')
        self.assertEqual(str(e.exception), 'No such file or directory: not_exist')

        with self.assertRaises(SharedFileException) as e:
            actual = get_download_src_dst_list('l0.csv', 'not_exist/local.csv')
        self.assertEqual(str(e.exception), 'No such file or directory: not_exist')

        with self.assertRaises(SharedFileException) as e:
            actual = get_download_src_dst_list('ln.csv', '.')
        self.assertEqual(str(e.exception), 'No such file or directory: /ln.csv')

    def norm_src_dst_list(self, pairs):
        return [(p[0], os.path.normpath(p[1])) for p in pairs]

    def test_normal_src_path(self):
        # normalize the user input source path
        self.assertEqual('/abc', _normalize_user_input_path('./abc'))
        self.assertEqual('/abc', _normalize_user_input_path('abc'))
        self.assertEqual('/', _normalize_user_input_path(''))
        self.assertEqual('/', _normalize_user_input_path('.'))
        self.assertEqual('/', _normalize_user_input_path('./'))
        self.assertEqual('.abc', _normalize_user_input_path('.abc'))

    def test_normal_dest_path(self):
        self.assertEqual('.', _normalize_dest_path(''))
        self.assertEqual('.', _normalize_dest_path('.'))
        self.assertEqual('.', _normalize_dest_path('./'))
        self.assertEqual('/', _normalize_dest_path('/'))
        self.assertEqual('abc', _normalize_dest_path('abc'))
        self.assertEqual('./abc', _normalize_dest_path('./abc'))
