from primehub.admin_users import validate, USERNAME_FORMAT_ERROR, EMAIL_FORMAT_ERROR
from primehub.utils import PrimeHubException
from tests import BaseTestCase


class TestAdminUsers(BaseTestCase):

    def setUp(self) -> None:
        super(TestAdminUsers, self).setUp()

    def check_required(self, cfg: dict, message: str, callback=None):
        with self.assertRaises(PrimeHubException) as context:
            if callback is None:
                validate(cfg)
            else:
                callback(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def test_required_field_validator(self):

        # check empty username
        self.check_required({}, 'username is required')

        # checkt bad username
        self.check_required({'username': '-abc'}, USERNAME_FORMAT_ERROR)
        self.check_required({'username': 'Upper-case'}, USERNAME_FORMAT_ERROR)

        # pass with valid usernames
        validate({'username': 'user1'})
        validate({'username': 'user1-a-b-d'})
        validate({'username': 'user1@abc.com'})

    def test_email_validator(self):

        payload = dict(username='user1')

        # pass without email
        validate(payload)

        # check bad mail format
        self.check_required({**payload, 'email': ''}, EMAIL_FORMAT_ERROR)
        self.check_required({**payload, 'email': 'email'}, EMAIL_FORMAT_ERROR)
        self.check_required({**payload, 'email': 'email@'}, EMAIL_FORMAT_ERROR)
        self.check_required({**payload, 'email': 'email@222.222.22'}, EMAIL_FORMAT_ERROR)

        # pass with valid email
        validate({**payload, 'email': 'email@example.com'})
