from functools import wraps

from primehub.utils import reject_action
from primehub.utils.decorators import __requires_permission__, logger, __command_groups__


def has_permission_flag(cmd_args: dict):
    k = "{}.{}".format(cmd_args['module'], cmd_args['func'])
    if k in __requires_permission__:
        return True
    return False


def disable_reject_action(action):
    logger.debug('@ask_for_permission is disable, the action will pass %s', action)


reject_action_function = disable_reject_action


def enable_ask_for_permission_feature():
    global reject_action_function
    reject_action_function = reject_action


def ask_for_permission(func):
    k = "{}.{}".format(func.__module__, func.__name__)
    __requires_permission__[k] = ""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not kwargs.get('--yes-i-really-mean-it', False):
            cmd_args = None
            try:
                actions = __command_groups__[func.__module__]
                cmd_args = [x for x in actions if x['func'] == func.__name__]
            except BaseException:
                pass
            if cmd_args:
                reject_action_function(cmd_args[0]['name'])
            else:
                reject_action_function(func.__name__)

        return func(*args, **kwargs)

    return wrapper
