import abc
import importlib
import json
import os
import sys
from typing import Union, Callable, Dict

from primehub.utils.decorators import cmd  # noqa: F401
from primehub.utils.http_client import Client


class NoSuchGroup(BaseException):
    pass


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
        self.config_file = kwargs.get('config', self.get_default_path())

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
            if os.path.exists(os.path.expanduser(self.config_file)):
                with open(self.config_file, "r") as fh:
                    self.config_from_file = json.load(fh)
        except BaseException:
            pass

    def load_config_from_env(self):
        # environment variables: PRIMEHUB_API_TOKEN, PRIMEHUB_API_ENDPOINT and PRIMEHUB_GROUP

        def set_env(key):
            if os.environ.get(key):
                self.config_from_env[key] = os.environ.get(key)

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

        with open(path or self.config_file, "w") as fh:
            fh.write(json.dumps(output))

    @property
    def group(self):
        if self.config_from_user_input.get('group', None):
            return self.config_from_user_input['group']
        if self.config_from_env.get('PRIMEHUB_GROUP', None):
            return self.config_from_env.get('PRIMEHUB_GROUP')
        if self.config_from_file.get('group', None) and self.config_from_file['group'].get('name', None):
            return self.config_from_file['group']['name']

    @group.setter
    def group(self, group):
        self.config_from_user_input['group'] = group

    @property
    def api_token(self):
        if self.config_from_user_input.get('api-token', None):
            return self.config_from_user_input['api-token']
        if self.config_from_env.get('PRIMEHUB_API_TOKEN', None):
            return self.config_from_env.get('PRIMEHUB_API_TOKEN')
        return self.config_from_file.get('api-token', None)

    @api_token.setter
    def api_token(self, api_token):
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
        self.config_from_user_input['endpoint'] = endpoint

    @property
    def current_group(self):
        return self.group_info

    @current_group.setter
    def current_group(self, group_info):
        self.group_info = group_info


class Helpful(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def help_description(self):
        """one line description for all commands"""
        return NotImplemented


class GraphQLException(BaseException):
    pass


class PrimeHub(object):

    def __init__(self, config: PrimeHubConfig):
        self.primehub_config = config
        self.commands: Dict[str, Module] = dict()
        self._stderr = sys.stderr
        self._stdout = sys.stdout

        # register commands
        self.register_command('config', 'Config')
        self.register_command('group', 'Group')
        self.register_command('images', 'Images')
        self.register_command('me', 'Me')

    def request(self, variables: dict, query: str):
        return Client(self.primehub_config).request(variables, query)

    def register_command(self, module_name: str, command_class: Union[str, Callable], command_name=None):
        if not command_name:
            command_name = module_name

        # create command instance
        if isinstance(command_class, str):
            clazz = importlib.import_module('primehub.' + module_name).__getattribute__(command_class)
        else:
            clazz = command_class
        cmd_group = self.commands[command_name] = clazz(self)

        # attach request method
        cmd_group.primehub_config = self.primehub_config
        cmd_group.request = self.request

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


class Module(object):

    def __init__(self, primehub: PrimeHub, **kwargs):
        self.primehub = primehub


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
