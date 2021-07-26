import abc
import importlib
import json
import os
from typing import Union, Callable

import requests

from primehub.utils.decorators import cmd


class PrimeHubConfig(dict):

    def __init__(self, **kwargs):
        super(PrimeHubConfig, self).__init__(**kwargs)

    def default_path(self):
        return os.path.expanduser("~/.primehub/sdk.json")

    def load_default_config(self):
        with open(self.default_path(), "r") as fh:
            for k, v in json.load(fh).items():
                self[k] = v

    def save(self, path=None):
        with open(path or self.default_path(), "w") as fh:
            fh.write(json.dumps(self))


class Helpful(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def help_description(self):
        """one line description for all commands"""
        return NotImplemented


class PrimeHub(object):

    def __init__(self, config: PrimeHubConfig):
        self.primehub_config = config
        self.commands = dict()

        # register commands
        self.register_command('config', 'Config')
        self.register_command('group', 'Group')
        self.register_command('me', 'Me')

    def request(self, variables: dict, query: str):
        request_body = dict(variables=json.dumps(variables), query=query)
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config['token'])}
        content = requests.post(self.primehub_config["endpoint"], data=request_body, headers=headers).text
        result = json.loads(content)
        return result

    def register_command(self, module_name: str, command_class: Union[str, Callable], command_name=None):
        if not command_name:
            command_name = module_name

        # create command instance
        if isinstance(command_class, str):
            clazz = importlib.import_module('primehub.' + module_name).__getattribute__(command_class)
        else:
            clazz = command_class
        cmd = self.commands[command_name] = clazz(self)

        # attach request method
        cmd.primehub_config = self.primehub_config
        cmd.request = self.request

    def __getattr__(self, item):
        if item in self.commands:
            return self.commands[item]
        raise AttributeError("Cannot find a command [{}]".format(item))


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
