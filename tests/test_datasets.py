from primehub.datasets import validate_creation, validate_update, get_phfs_path, protect_metadata
from primehub.utils import PrimeHubException, DatasetsException
from tests import BaseTestCase


class TestDatasets(BaseTestCase):

    def setUp(self) -> None:
        super(TestDatasets, self).setUp()

    def check_exception(self, cfg: dict, message: str, validator):
        with self.assertRaises(PrimeHubException) as context:
            validator(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def test_creation_validator(self):
        invalid_id_format_msg = "id should be string type and lower case alphanumeric characters, '-' or '.'. " \
                                "The value must start and end with an alphanumeric character " \
                                "and its length of it should be less than 63."

        self.check_exception({}, 'id is a required field', validate_creation)
        self.check_exception({'id': 123}, invalid_id_format_msg, validate_creation)
        self.check_exception({'id': '^.<', 'groupName': 'my-group'}, invalid_id_format_msg, validate_creation)
        self.check_exception({'id': '1_2_3', 'groupName': 'my-group'}, invalid_id_format_msg, validate_creation)

        self.check_exception({'id': 'dataset-1', 'tags': [123], 'groupName': 'my-group'},
                             'The value of the tags should be a list of string.', validate_creation)
        self.check_exception({'id': 'dataset-1', 'tags': ['tag-1', 123], 'groupName': 'my-group'},
                             'The value of the tags should be a list of string.', validate_creation)

        # pass with valid configuration
        validate_creation({'id': 'dataset-1', 'groupName': 'my-group'})
        validate_creation({'id': 'dataset-1', 'groupName': 'my-group', 'tags': ['tag-1', 'tag-2']})

    def test_update_validator(self):
        self.check_exception({'tags': [123], 'groupName': 'my-group'},
                             'The value of the tags should be a list of string.', validate_update)
        self.check_exception({'tags': ['tag-1', 123], 'groupName': 'my-group'},
                             'The value of the tags should be a list of string.', validate_update)

        # pass with valid configuration
        validate_update({})
        validate_update({'tags': ['tag-1', 'tag-2']})

    def test_gen_datasets_path(self):
        self.assertEqual(get_phfs_path('dataset-1', '/'), '/datasets/dataset-1/')
        self.assertEqual(get_phfs_path('dataset-1', './'), '/datasets/dataset-1/')
        self.assertEqual(get_phfs_path('dataset-1', '.'), '/datasets/dataset-1/')
        self.assertEqual(get_phfs_path('dataset-1', '.abc'), '/datasets/dataset-1/.abc')
        self.assertEqual(get_phfs_path('dataset-1', './a/../.abc'), '/datasets/dataset-1/a/../.abc')
        self.assertEqual(get_phfs_path('dataset-1', '///a/../.abc'), '/datasets/dataset-1///a/../.abc')

    def test_protect_metadata(self):
        dataset = 'dataset-1'
        # path to metadata
        with self.assertRaises(DatasetsException) as e:
            protect_metadata(dataset, get_phfs_path(dataset, '/.dataset'))
        self.assertEqual('Invalid Operation', str(e.exception))

        with self.assertRaises(DatasetsException) as e:
            protect_metadata(dataset, get_phfs_path(dataset, '//.dataset'))
        self.assertEqual('Invalid Operation', str(e.exception))

        with self.assertRaises(DatasetsException) as e:
            protect_metadata(dataset, get_phfs_path(dataset, '.dataset'))
        self.assertEqual('Invalid Operation', str(e.exception))

        with self.assertRaises(DatasetsException) as e:
            protect_metadata(dataset, get_phfs_path(dataset, './a/../.dataset'))
        self.assertEqual('Invalid Operation', str(e.exception))

        with self.assertRaises(DatasetsException) as e:
            protect_metadata(dataset, get_phfs_path(dataset, './.dataset'))
        self.assertEqual('Invalid Operation', str(e.exception))

        with self.assertRaises(DatasetsException) as e:
            protect_metadata(dataset, get_phfs_path(dataset, '///a/../.dataset'))
        self.assertEqual('Invalid Operation', str(e.exception))

        with self.assertRaises(DatasetsException) as e:
            protect_metadata(dataset, get_phfs_path(dataset, '///a/..//.dataset'))
        self.assertEqual('Invalid Operation', str(e.exception))

        # pass with valid path
        protect_metadata(dataset, get_phfs_path(dataset, '/test.csv'))
        protect_metadata(dataset, get_phfs_path(dataset, '/dataset.csv'))
        protect_metadata(dataset, get_phfs_path(dataset, '/.data'))
        protect_metadata(dataset, get_phfs_path(dataset, '/dataset'))
        protect_metadata(dataset, get_phfs_path(dataset, '/.dataset.dataset'))
        protect_metadata(dataset, get_phfs_path(dataset, '/deep/.dataset'))
