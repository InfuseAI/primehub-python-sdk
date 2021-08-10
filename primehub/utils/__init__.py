import logging
import os
import sys


class PrimeHubException(BaseException):
    pass


class GroupIsRequiredException(PrimeHubException):
    pass


class UserRejectAction(PrimeHubException):
    pass


class RequestException(PrimeHubException):
    pass


class ResponseException(PrimeHubException):
    pass


def reject_action(action):
    raise UserRejectAction(
        'User rejects action [%s], please use the flag "--yes-i-really-mean-it" to allow the action.' % action)


def group_required():
    raise GroupIsRequiredException('No group information, please configure the active group first.')


def group_not_found(group):
    raise GroupIsRequiredException('No group information for [%s], please check the configuration again.' % group)


def create_logger(name) -> logging.Logger:
    log_level = logging.WARNING
    if os.environ.get('PRIMEHUB_SDK_LOG_LEVEL') == 'DEBUG':
        log_level = logging.DEBUG
    if os.environ.get('PRIMEHUB_SDK_LOG_LEVEL') == 'INFO':
        log_level = logging.INFO

    log = logging.getLogger(name)
    log.setLevel(log_level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log
