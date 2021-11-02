from primehub.admin_images import validate, validate_image_type, validate_image_spec
from primehub.utils import PrimeHubException
from tests import BaseTestCase


class TestAdminImages(BaseTestCase):

    def setUp(self) -> None:
        super(TestAdminImages, self).setUp()

    def check_required(self, cfg: dict, message: str, callback=None):
        with self.assertRaises(PrimeHubException) as context:
            if callback is None:
                validate(cfg)
            else:
                callback(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def test_validator(self):

        # check empty username
        self.check_required({}, 'name is required')
        self.check_required({'name': 'aaaa_aaa'},
                            "[name] should be lower case alphanumeric characters, '-' "
                            "or '.', and must start and end with an alphanumeric character.")

        # check invalid type valuez
        self.check_required({'name': 'image-1', 'type': ''}, "type should be one of ['cpu', 'gpu', 'both']",
                            validate_image_type)
        self.check_required({'name': 'image-1', 'type': 'abc'}, "type should be one of ['cpu', 'gpu', 'both']",
                            validate_image_type)

        # TODO check secret useImagePullSecret after we support the "secrets" command group

        # check url* and imageSpec
        self.check_required({'name': 'image-1', 'url': 'image', 'imageSpec': {
            'baseImage': 'jupyter/base-notebook', 'packages': {'pip': ['pytest']}
        }}, "imageSpec cannot use with url and urlForGpu")

        self.check_required({'name': 'image-1', 'urlForGpu': 'image-for-gpu', 'imageSpec': {
            'baseImage': 'jupyter/base-notebook', 'packages': {'pip': ['pytest']}
        }}, "imageSpec cannot use with url and urlForGpu")

        # pass with valid configuration
        validate({'name': 'my-image.org'})

        # pass with url and urlForGpu
        validate({'name': 'my-image', 'url': 'image-url', 'urlForGpu': 'image-gpu-url'})

        # pass with imageSpec
        validate({'name': 'my-image', 'imageSpec': {
            'baseImage': 'jupyter/base-notebook', 'packages': {'pip': ['pytest']}
        }})

    def test_image_spec_validator(self):
        def s(cfg: dict):
            cfg['baseImage'] = 'jupyter/base-notebook'
            return cfg

        def c(payload: dict, expected: str):
            self.check_required(payload, expected, validate_image_spec)

        c({'name': 'image-1', 'imageSpec': {}}, "Invalid imageSpec: baseImage is required")
        c({'name': 'image-1', 'imageSpec': s({})}, "Invalid imageSpec: packages is required")

        c({'name': 'image-1', 'imageSpec': s({
            'packages': []
        })}, "Invalid imageSpec: packages is required")

        c({'name': 'image-1', 'imageSpec': s({
            'packages': {}
        })}, "Invalid imageSpec: packages is required")

        c({'name': 'image-1', 'imageSpec': s({
            'packages': ['pytest']}
        )}, "Invalid imageSpec: packages is a dict with {apt, pip, conda} keys and you have use at least one")

        c({'name': 'image-1', 'imageSpec': s({
            'packages': {'abc': ['abc']}
        })}, "Invalid imageSpec: packages is a dict with {apt, pip, conda} keys and you have use at least one")

        c({'name': 'image-1', 'imageSpec': s({
            'packages': {'pip': 'pytest'}
        })}, "Invalid imageSpec: packages values should be a list")
