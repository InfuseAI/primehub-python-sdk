import json
from tests import BaseTestCase


class TestCmdImages(BaseTestCase):
    """
    Usage:
      primehub images [command]

    Get a image or list images

    Available Commands:
      list                 List images
      get                  Get image by name
    """

    def setUp(self) -> None:
        super(TestCmdImages, self).setUp()
        self.image_info = [
          {
            "id": "tf-1",
            "name": "tf-1",
            "displayName": "TensorFlow 1.15.4 (Python 3.7)",
            "description": "TensorFlow 1.15.4 (Python 3.7)",
            "useImagePullSecret": None,
            "spec": {
              "description": "TensorFlow 1.15.4 (Python 3.7)",
              "displayName": "TensorFlow 1.15.4 (Python 3.7)",
              "type": "both",
              "url": "infuseai/docker-stacks:tensorflow-notebook-v1-15-4-dbdcead1",
              "urlForGpu": "infuseai/docker-stacks:tensorflow-notebook-v1-15-4-dbdcead1-gpu"
            }
          }
        ]

    def test_images_list(self):
        self.sdk.primehub_config.group = 'fake-group'

        self.mock_request.return_value = {'data': {'me': {'effectiveGroups': [
          {'name': 'fake-group', 'images': self.image_info}]}}
        }

        args = ['app.py', 'images', 'list']
        out = self.cli_stdout(args)
        self.assertEqual(json.loads(out), self.image_info)

    def test_images_get(self):
        self.sdk.primehub_config.group = 'fake-group'

        self.mock_request.return_value = {'data': {'me': {'effectiveGroups': [
          {'name': 'fake-group', 'images': self.image_info}]}}
        }

        args = ['app.py', 'images', 'get', 'tf-1']
        out = self.cli_stdout(args)
        self.assertEqual(json.loads(out), self.image_info[0])

    def test_images_get_not_found(self):
        self.sdk.primehub_config.group = 'fake-group'

        self.mock_request.return_value = {'data': {'me': {'effectiveGroups': [
          {'name': 'fake-group', 'images': self.image_info}]}}
        }

        args = ['app.py', 'images', 'get', 'tf-not-found']
        out = self.cli_stdout(args)
        self.assertEqual(out, '')
