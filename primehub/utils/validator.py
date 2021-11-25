import json
import re
from typing import Union, Any, Optional, Dict, List

from primehub.utils import PrimeHubException

PV_GROUP_CONNECT_ERROR = 'group connect should be a pair {id, writable}'
GROUP_CONNECT_ERROR = 'group connect should be an entry {id}'
GROUP_DISCONNECT_ERROR = 'disconnect connect should be an entry {id}'


def validate_name(payload: dict):
    if 'name' not in payload:
        raise PrimeHubException('name is required')

    matched: Union[str, Any, None] = re.match(
        r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$',
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


def validate_connection(payload: dict, field_name: str):
    CONNECT_ERROR = f'{field_name} connection payload should be an entry {{id}}'
    DISCONNECT_ERROR = f'{field_name} disconnection payload should be an entry {{id}}'

    if field_name not in payload:
        return

    # check connection format
    connection: Optional[Dict[Any, Any]] = payload.get(field_name)
    if connection:
        connection_payload = connection.get('connect', [])
        if not isinstance(connection_payload, list):
            raise PrimeHubException('connection should be list type')

        for entry in connection_payload:
            if not isinstance(entry, dict):
                raise PrimeHubException(CONNECT_ERROR)
            if 'id' in entry and len(entry) == 1:
                continue
            raise PrimeHubException(CONNECT_ERROR)

        disconnection_payload = connection.get('disconnect', [])
        if not isinstance(disconnection_payload, list):
            raise PrimeHubException('disconnection should be list type')

        for entry in disconnection_payload:
            if not isinstance(entry, dict):
                raise PrimeHubException(DISCONNECT_ERROR)
            if 'id' in entry and len(entry) == 1:
                continue
            raise PrimeHubException(DISCONNECT_ERROR)


class Validator(object):
    class OpBase:
        def __init__(self, acceptable_types: list):
            self.types = acceptable_types

        def validate(self, value):
            for x in self.types:
                if isinstance(value, x):
                    return True
            return False

        def error_message(self, field: str):
            t = [x.__name__ for x in self.types]
            if len(self.types) == 1:
                return f'The value of the {field} should be the {t[0]} type'
            else:
                return f'The value of the {field} should be one of the types: [{", ".join(t)}]'

    class OpID(OpBase):
        def __init__(self):
            super().__init__([str])

    class OpString(OpBase):

        def __init__(self):
            super().__init__([str])

    class OpInt(OpBase):

        def __init__(self):
            super().__init__([int])

        def validate(self, value):
            # Int also consider as bool, but not suitable to our use cases
            if isinstance(value, bool):
                return False

            for x in self.types:
                if isinstance(value, x):
                    return True
            return False

    class OpIntGe0(OpInt):

        def validate(self, value):
            if not super().validate(value):
                return False
            return value >= 0

        def error_message(self, field: str):
            return f'The value of the {field} should be an integer value >= 0'

    class OpFloat(OpBase):
        def __init__(self):
            super().__init__([int, float])

        def validate(self, value):
            # Int also consider as bool, but not suitable to our use cases
            if isinstance(value, bool):
                return False

            for x in self.types:
                if isinstance(value, x):
                    return True
            return False

    class OpJSON(OpBase):
        def __init__(self):
            super().__init__([dict])

    class OpPhAppScope(OpBase):
        def __init__(self):
            super().__init__([str])
            self.scope_list = ['public', 'primehub', 'group']

        def validate(self, value):
            return value in self.scope_list

        def error_message(self, field: str):
            return f'The value of the {field} should be one of [{", ".join(self.scope_list)}]'

    class OpEnvList(OpBase):
        def __init__(self):
            super().__init__([list])

        def validate(self, value):
            if not isinstance(value, list):
                return False
            for entry in value:
                if not isinstance(entry, dict):
                    return False
                if sorted(entry.keys()) != sorted(['name', 'value']):
                    return False
                if not isinstance(entry['value'], str):
                    return False
            return True

        def error_message(self, field: str):
            example = [
                dict(name="name", value="my-name"),
                dict(name="int_value", value="1"),
                dict(name="float_value", value="1.5"),
                dict(name="bool_value", value="true"),
            ]
            return f'The value of the {field} should be an EnvList. ' \
                   f'It is a list of {{name, value}} and all values MUST be a string.\n' \
                   f'For example: {json.dumps(example)}'

    def __init__(self, type_def: str):
        self.type_def = type_def
        self.type_name = type_def.replace('!', '')
        self.required = type_def.endswith('!')
        self.typeOp = getattr(self, f'Op{self.type_name}')

    def validate(self, value):
        return self.typeOp().validate(value)

    def error_message(self, error_field: str):
        return self.typeOp().error_message(error_field)


class ValidationSpec(object):

    def __init__(self, validation_spec: str):
        self.validation_spec = validation_spec
        self._required_fields: List = []
        self._fields: List = []
        self._process_fields()

    def _process_fields(self):
        for line in self.validation_spec.strip().split('\n'):
            if ':' not in line:
                continue
            field, type_def = [x.strip() for x in line.strip().split(':')]
            if type_def.endswith('!'):
                self._required_fields.append((field, Validator(type_def)))
            self._fields.append((field, Validator(type_def)))

    def required_fields(self):
        return [(name, type_def) for name, type_def in self._required_fields]

    def get_field(self, field):
        for f, v in self._fields:
            if field == f:
                return v
        return None

    def validate(self, data: dict):
        def check_type(validator, field: str, value: Any):
            if validator.validate(value):
                return
            raise PrimeHubException(validator.error_message(field))

        for field, validator in self._required_fields:
            if field not in data:
                raise PrimeHubException(f'{field} is a required field')
            value = data[field]
            if value is None:
                raise PrimeHubException(f'{field} can not be null, it is a required field')
            check_type(validator, field, data[field])

        for field, validator in self._fields:
            if field not in data:
                continue
            if data[field] is None:
                continue
            check_type(validator, field, data[field])
