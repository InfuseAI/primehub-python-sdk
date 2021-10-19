import re
from typing import Union, Any, Optional, Dict

from primehub.utils import PrimeHubException

PV_GROUP_CONNECT_ERROR = 'group connect should be a pair {id, writable}'
GROUP_CONNECT_ERROR = 'group connect should be an entry {id}'
GROUP_DISCONNECT_ERROR = 'disconnect connect should be an entry {id}'


def validate_name(payload: dict):
    if 'name' not in payload:
        raise PrimeHubException('name is required')

    matched: Union[str, Any, None] = re.match(
        r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*',
        payload.get('name'))

    # check formats
    if not matched:
        raise PrimeHubException("[name] should be lower case alphanumeric characters, '-' or '.', "
                                "and must start and end with an alphanumeric character.")


def validate_pv_groups(payload: dict):
    if 'groups' not in payload:
        return

    # check groups format
    groups: Optional[Dict[Any, Any]] = payload.get('groups')
    if groups:
        for g in groups.get('connect', []):
            if not isinstance(g, dict):
                raise PrimeHubException(PV_GROUP_CONNECT_ERROR)
            if 'id' in g and 'writable' in g:
                continue
            raise PrimeHubException(PV_GROUP_CONNECT_ERROR)

        for g in groups.get('disconnect', []):
            if not isinstance(g, dict):
                raise PrimeHubException(GROUP_DISCONNECT_ERROR)
            if 'id' in g and len(g) == 1:
                continue
            raise PrimeHubException(GROUP_DISCONNECT_ERROR)


def validate_groups(payload: dict):
    if 'groups' not in payload:
        return

    # check groups format
    groups: Optional[Dict[Any, Any]] = payload.get('groups')
    if groups:
        for g in groups.get('connect', []):
            if not isinstance(g, dict):
                raise PrimeHubException(GROUP_CONNECT_ERROR)
            if 'id' in g and len(g) == 1:
                continue
            raise PrimeHubException(GROUP_CONNECT_ERROR)

        for g in groups.get('disconnect', []):
            if not isinstance(g, dict):
                raise PrimeHubException(GROUP_DISCONNECT_ERROR)
            if 'id' in g and len(g) == 1:
                continue
            raise PrimeHubException(GROUP_DISCONNECT_ERROR)
