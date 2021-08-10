from functools import wraps
from inspect import signature
from types import FunctionType
from typing import Dict

from primehub.utils import create_logger
from primehub.utils.optionals import default_optional_builder

logger = create_logger('decorator')

__command_groups__: Dict[str, list] = dict()
__actions__: Dict[str, dict] = dict()
__requires_permission__: Dict[str, str] = dict()


def find_actions(sub_command):
    m = sub_command.__module__
    if m in __command_groups__:
        actions = __command_groups__[m]
        from operator import itemgetter
        return sorted(actions, key=itemgetter('name'))
    return []


def _a(module, action):
    return "{}.{}".format(module.__module__, action)


def find_action_info(module, action):
    logger.debug("find_action_info (%s, %s)", module, action)
    if _a(module, action) in __actions__:
        return __actions__[_a(module, action)]


def find_action_method(module, action):
    info = find_action_info(module, action)
    if info:
        return info['func']


def register_to_command_group(func, cmd_args):
    """
    A python module is a .py file, there are one or more commands in a module.
    A module is a command group with lots of actions and each action is a method in the module.

    For example:
    module cli_config could have {set_endpoint, set_token_, set_group} actions.

    We keep:
     * an action with the key "<modulde>.<action>" for O(1) action search.
     * an module with the key "<module>" for O(1) module-actions search
    """

    if func.__module__ not in __command_groups__:
        __command_groups__[func.__module__] = []

    __command_groups__[func.__module__].append(cmd_args)
    __actions__["{}.{}".format(func.__module__, cmd_args['name'])] = cmd_args


def cmd(**cmd_args):
    if 'name' not in cmd_args:
        raise ValueError('name field is required')
    if 'description' not in cmd_args:
        raise ValueError('name description is required')
    if 'optionals' not in cmd_args:
        cmd_args['optionals'] = []
    if 'return_required' not in cmd_args:
        cmd_args['return_required'] = False

    for idx, opts in enumerate(cmd_args['optionals']):
        maybe_builder = opts[-1]
        if not isinstance(maybe_builder, FunctionType):
            cmd_args['optionals'][idx] = tuple(list(opts) + [default_optional_builder])

    def inner(func):
        make_command_references(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def make_command_references(func):
        # TODO only generate references when invoked from primehub-cli
        cmd_args['module'] = func.__module__
        cmd_args['func'] = func.__name__
        sig = signature(func)
        import inspect

        def info(x):
            if x.annotation is inspect.Parameter.empty:
                t = str
            else:
                t = x.annotation
            return x.name, t, str(x.kind) == 'VAR_KEYWORD',

        cmd_args['arguments'] = [info(x) for x in sig.parameters.values() if x.name != 'self']
        logger.debug("cmd -> %s", cmd_args)
        register_to_command_group(func, cmd_args)

    return inner


def show_debug_info():
    print("Command Groups:")
    for k, v in __command_groups__.items():
        print("  {}".format(k))
        for a in v:
            print("    {}".format(a))
    print("")
    print("Actions:")
    for k, v in __actions__.items():
        print("  {}\n    {}".format(k, v))
    print("")
    print("Permission:")
    for k, v in __requires_permission__.items():
        print("  {}".format(k))
    print("")


class Command(object):

    def __init__(self, name, description, optional_arguments: list):
        self.name = name
        self.description = description
        self.optional_arguments = optional_arguments
