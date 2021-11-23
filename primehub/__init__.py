import abc
import importlib
import json
import os
import sys
from typing import Union, Callable, Any

from primehub.utils import group_required, create_logger, PrimeHubException
from primehub.utils.core import CommandContainer
from primehub.utils.decorators import cmd  # noqa: F401
from primehub.utils.display import Display, HumanFriendlyDisplay, Displayable
from primehub.utils.http_client import Client

logger = create_logger('primehub-config')


def _get_version():
    version_file = os.path.normpath(os.path.join(os.path.dirname(__file__), 'VERSION'))
    with open(version_file) as fh:
        version = fh.read().strip()
        return version


__version__ = _get_version()


class PrimeHubConfig(object):
    """
    PrimeHubConfig load the config from the default path ~/.primehub/config.json

    The config.json looks like:
    {
       "endpoint": ""
       "api-token": "",
       "group": {
          "id": "",
          "name": "",
          "displayName": "",
       }
    }

    PrimeHubConfig allows changing setting from four ways:
    * the default config path
    * alternative path for the config file (config argument from constructor)
    * environment variables: PRIMEHUB_API_TOKEN, PRIMEHUB_API_ENDPOINT and PRIMEHUB_GROUP
    * set property for api_token, endpoint and group

    PrimeHubConfig evaluates a property in the above order and the last updates take effect
    """

    def __init__(self, **kwargs):
        self.config_file = kwargs.get('config', None)
        if not self.config_file:
            self.config_file = self.get_default_path()

        # PrimeHub SDK evaluate
        self.config_from_file = {}
        self.config_from_env = {}
        self.config_from_user_input = {}
        self.group_info = {}

        self.load_config()
        self.load_config_from_env()
        self.set_properties(**kwargs)

    def set_properties(self, **kwargs):
        if kwargs.get('group', None):
            self.group = kwargs['group']
        if kwargs.get('token', None):
            self.api_token = kwargs['token']
        if kwargs.get('endpoint', None):
            self.endpoint = kwargs['endpoint']

    def load_config(self):
        try:
            if not os.path.exists(os.path.expanduser(self.config_file)):
                return
            with open(self.config_file, "r") as fh:
                self.config_from_file = json.load(fh)
                if self.config_from_file and 'group' in self.config_from_file:
                    self.group_info = self.config_from_file['group']
        except BaseException:
            pass

    def load_config_from_env(self):
        # environment variables: PRIMEHUB_API_TOKEN, PRIMEHUB_API_ENDPOINT and PRIMEHUB_GROUP

        def set_env(key):
            if os.environ.get(key):
                self.config_from_env[key] = os.environ.get(key)
                if key == 'PRIMEHUB_GROUP' and self.group_info:
                    self.group_info['name'] = os.environ.get(key)

        set_env('PRIMEHUB_API_TOKEN')
        set_env('PRIMEHUB_API_ENDPOINT')
        set_env('PRIMEHUB_GROUP')

    def get_default_path(self):
        return os.path.expanduser("~/.primehub/config.json")

    def save(self, path=None):
        """
        The config.json looks like:
        {
           "endpoint": ""
           "api-token": "",
           "group": {
              "id": "",
              "name": "",
              "displayName": "",
           }
        }
        """
        output = dict()
        output['endpoint'] = self.endpoint
        output['api-token'] = self.api_token
        if self.group_info and self.group_info.get('name', None) == self.group:
            output['group'] = self.group_info
        else:
            output['group'] = dict(name=self.group)

        output_path = os.path.expanduser(path or self.config_file)
        if os.path.dirname(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as fh:
            fh.write(json.dumps(output, indent=2, sort_keys=True))

    @property
    def group(self):
        if self.config_from_user_input.get('group', None):
            logger.debug('group config_from_user_input')
            return self.config_from_user_input['group']
        if self.config_from_env.get('PRIMEHUB_GROUP', None):
            logger.debug('group config_from_env')
            return self.config_from_env.get('PRIMEHUB_GROUP')
        if self.config_from_file.get('group', None) and self.config_from_file['group'].get('name', None):
            logger.debug('group config_from_file')
            return self.config_from_file['group']['name']

    @group.setter
    def group(self, group):
        if group:
            self.config_from_user_input['group'] = group
            if self.group_info:
                self.group_info['name'] = group

    @property
    def api_token(self):
        if self.config_from_user_input.get('api-token', None):
            return self.config_from_user_input['api-token']
        if self.config_from_env.get('PRIMEHUB_API_TOKEN', None):
            return self.config_from_env.get('PRIMEHUB_API_TOKEN')
        return self.config_from_file.get('api-token', None)

    @api_token.setter
    def api_token(self, api_token):
        if api_token:
            self.config_from_user_input['api-token'] = api_token

    @property
    def endpoint(self):
        if self.config_from_user_input.get('endpoint', None):
            return self.config_from_user_input['endpoint']
        if self.config_from_env.get('PRIMEHUB_API_ENDPOINT', None):
            return self.config_from_env.get('PRIMEHUB_API_ENDPOINT')
        return self.config_from_file.get('endpoint', None)

    @endpoint.setter
    def endpoint(self, endpoint):
        if endpoint:
            self.config_from_user_input['endpoint'] = endpoint

    @property
    def current_group(self) -> dict:
        return self.group_info

    @current_group.setter
    def current_group(self, group_info):
        if group_info and group_info.get('id', None):
            self.group_info = group_info


class Helpful(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def help_description(self):
        """one line description for all commands"""
        return NotImplemented


class PrimeHub(object):

    def __init__(self, config: PrimeHubConfig):
        self.primehub_config = config
        self.json_output = True
        self.usage_role = 'user'
        self.commands: CommandContainer = CommandContainer()
        self.admin_commands: CommandContainer = CommandContainer()
        self._stderr = sys.stderr
        self._stdout = sys.stdout

        # register commands
        self.register_command('config', 'Config')
        self.register_command('groups', 'Groups')
        self.register_command('images', 'Images')
        self.register_command('volumes', 'Volumes')
        self.register_command('instancetypes', 'InstanceTypes')
        self.register_command('jobs', 'Jobs')
        self.register_command('recurring_jobs', 'RecurringJobs', 'recurring-jobs')
        self.register_command('deployments', 'Deployments')
        self.register_command('notebooks', 'Notebooks')
        self.register_command('files', 'Files')
        self.register_command('me', 'Me')
        self.register_command('version', 'Version')
        self.register_command('apptemplates', 'AppTemplate')
        self.register_command('apps', 'Apps')
        self.register_command('models', 'Models')
        self.register_dummy_command('admin', 'Commands for system administrator')

        # register admin commands
        self.register_admin_command('admin_images', 'AdminImages', 'images')
        self.register_admin_command('admin_volumes', 'AdminVolumes', 'volumes')
        self.register_admin_command('admin_instancetypes', 'AdminInstanceTypes', 'instancetypes')
        self.register_admin_command('admin_users', 'AdminUsers', 'users')
        self.register_admin_command('admin_groups', 'AdminGroups', 'groups')

        # initial
        self._ensure_config_details(config)

    def _ensure_config_details(self, config: PrimeHubConfig):
        try:
            group_id = config.current_group.get('id', None)
            group_name = config.current_group.get('name', None)
            if group_name is None:
                return

            if group_id is None:
                self.config.reconfigure_group(group_name)
        except BaseException:
            pass

    def request(self, variables: dict, query: str, error_handler: Callable = None):
        return Client(self.primehub_config).request(variables, query, error_handler)

    def request_logs(self, endpint: str, follow: bool, tail: int):
        return Client(self.primehub_config).request_logs(endpint, follow, tail)

    def request_file(self, endpint: str, dest: str):
        return Client(self.primehub_config).request_file(endpint, dest)

    def upload_file(self, endpoint: str, src: str):
        return Client(self.primehub_config).upload_file(endpoint, src)

    def _find_command_class(self, command_class, module_name):
        # create command instance
        if isinstance(command_class, str):
            clazz = importlib.import_module('primehub.' + module_name).__getattribute__(command_class)
        else:
            clazz = command_class
        return clazz

    def register_dummy_command(self, command_name, command_help):

        # register to the commands table
        self.commands[command_name] = Dummy(self, command_help)

    def register_command(self, module_name: str, command_class: Union[str, Callable], command_name=None):
        self._register_command(self.commands, module_name, command_class, command_name)

    def register_admin_command(self, module_name: str, command_class: Union[str, Callable], command_name=None):
        self._register_command(self.admin_commands, module_name, command_class, command_name)

    def _register_command(self, target, module_name: str, command_class: Union[str, Callable], command_name=None):
        clazz = self._find_command_class(command_class, module_name)

        # register to the commands table
        module_object = clazz(self)
        if module_name and command_name:
            target[f':{module_name}'] = module_object
            target[command_name] = module_object
        else:
            target[module_name] = module_object

    def switch_admin_role(self):
        self.usage_role = 'admin'
        self.commands = self.admin_commands

    @property
    def admin(self):
        admin_primehub = PrimeHub(self.primehub_config)
        admin_primehub.commands = self.admin_commands
        return admin_primehub

    def __getattr__(self, item):
        if item in self.commands:
            return self.commands[item]
        raise AttributeError("Cannot find a command [{}]".format(item))

    @property
    def stderr(self):
        return self._stderr

    @stderr.setter
    def stderr(self, out):
        self._stderr = out

    @property
    def stdout(self):
        return self._stdout

    @stdout.setter
    def stdout(self, out):
        self._stdout = out

    def get_all_commands(self):
        return sorted(self.commands.keys())

    def is_ready(self):
        if self.primehub_config.current_group is None:
            return False
        if not self.primehub_config.current_group.get('id', None):
            return False
        return True

    @property
    def current_group(self) -> dict:
        g = self.primehub_config.current_group
        if not g:
            group_required()
        if not g.get('id', None):
            group_required()
        return g

    @property
    def group_id(self) -> str:
        return self.current_group['id']

    @property
    def group_name(self) -> str:
        return self.current_group['name']


class Module(object):

    def __init__(self, primehub: PrimeHub, **kwargs):
        self.primehub = primehub

        # attach request method
        self.request = primehub.request
        self.request_logs = primehub.request_logs
        self.request_file = primehub.request_file
        self.upload_file = primehub.upload_file

    @property
    def current_group(self) -> dict:
        return self.primehub.current_group

    @property
    def group_id(self) -> str:
        return self.primehub.group_id

    @property
    def group_name(self) -> str:
        return self.primehub.group_name

    @property
    def endpoint(self) -> str:
        return self.primehub.primehub_config.endpoint

    @property
    def primehub_config(self):
        raise ValueError(
            'The attribute [primehub_config] is access denied, '
            'please use props of the Module to get configurations')

    def get_display(self) -> Displayable:
        if self.primehub.json_output:
            return Display()
        else:
            return HumanFriendlyDisplay()

    def display(self, action: dict, value: Any):
        self.get_display().display(action, value, self.primehub.stdout)

    @staticmethod
    def output(result: dict, object_path: str):
        """
        Give a dict {'data': {'a': {'b': 'c'}}}
        we could get the c by the path a.b
        """
        if 'data' not in result:
            return result

        data = result.get('data')
        if not data:
            return result

        root: dict = dict()
        if isinstance(data, dict):
            root = data
        else:
            raise PrimeHubException('Unsupported data format')

        paths = object_path.split('.')
        for p in paths:
            if p not in root:
                raise PrimeHubException(f'Cannot access to the path {object_path}')
            root = root[p]

        return root


class Dummy(Helpful, Module):
    """
    Dummy subcommand
    """
    description = None

    def __init__(self, primehub: PrimeHub, description):
        super(Dummy, self).__init__(primehub)
        self.description = description

    def help_description(self):
        return self.description


def has_data_from_stdin():
    """
    Check if any data comes from stdin.

    :return: True if there are data from stdin, otherwise False
    """
    import sys
    import select

    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        return True
    else:
        return False


def primehub_load_config(filename):
    if has_data_from_stdin():
        return json.loads("".join(sys.stdin.readlines()))

    if filename and os.path.exists(filename):
        with open(filename, 'r') as fh:
            return json.load(fh)

    return {}
