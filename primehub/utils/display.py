import json

from types import GeneratorType
from typing import Any, TextIO, Union, Dict, List

from tabulate import tabulate

from primehub import create_logger
from abc import ABCMeta, abstractmethod

logger = create_logger('display')

CUSTOMIZED_COLUMNS: Dict[str, List[tuple]] = {
    'primehub.jobs.list': [
        ('id',),
        ('displayName',),
        ('schedule',),
        ('userName', 'user',),
        ('startTime',),
        ('finishTime',),
        ('phase',),
    ],
    'primehub.schedules.list': [
        ('id',),
        ('displayName',),
        ('recurrence',),
        ('userName', 'createdBy',),
        ('nextRunTime',),
    ],
    'primehub.images.list': [
        ('name',),
        ('displayName',),
        ('description',),
    ],
    'primehub.deployments.list': [
        ('id',),
        ('name',),
        ('modelImage',),
        ('description',),
        ('stop',),
        ('status',),
        ('message',),
    ]
}


def display_tree_like_format(data, file: TextIO, width=0, indent=0):
    output = data.items()
    if width == 0:
        width = 2 + max([len(x[0]) for x in output])
        if width < 15:
            width = 15

    for k, v in output:
        remaining = width - len(k)
        if isinstance(v, dict):
            print("{}{}:".format(" " * indent, k), file=file)
            display_tree_like_format(v, file, width - 2, indent + 2)
        else:
            print("{}{}:{}{}".format(" " * indent, k, " " * remaining, v), file=file)


class Displayable(metaclass=ABCMeta):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def display(self, action: dict, value: Any, file: TextIO):
        pass

    @abstractmethod
    def display_many(self, action: dict, value: Union[dict, list], file: TextIO):
        pass

    @abstractmethod
    def display_single(self, action: dict, value: Any, file: TextIO):
        pass


def wrapper_generator(gen):
    is_type_sent = False
    for x in gen:
        if not is_type_sent:
            yield isinstance(x, (str, bytes))
            is_type_sent = True
        yield x


class Display(Displayable):

    @property
    def name(self):
        return 'json'

    def display(self, action: dict, value: Any, file: TextIO):
        if not value:
            return
        logger.debug('use display %s', self.name)

        if isinstance(value, GeneratorType):
            logger.debug('display generator-type')
            wrapped_generator = wrapper_generator(value)
            is_str = next(wrapped_generator, None)
            if is_str is None:
                return
            if is_str:
                for x in wrapped_generator:
                    self.display_single(action, x, file)
            else:
                self.display(action, list(wrapped_generator), file)
        else:
            if isinstance(value, dict) or isinstance(value, list):
                self.display_many(action, value, file)
            else:
                self.display_single(action, value, file)

    def display_many(self, action: dict, value: Union[dict, list], file: TextIO):
        logger.debug('display-many')
        json.dump(value, file)

    def display_single(self, action: dict, value: Any, file: TextIO):
        logger.debug('display-single')
        if isinstance(value, str):
            print(value, file=file)
        elif isinstance(value, bytes):
            file.write(value.decode())
        else:
            json.dump(value, file)


class HumanFriendlyDisplay(Displayable):

    @property
    def name(self):
        return 'human-friendly'

    def display(self, action: dict, value: Any, file: TextIO):
        if not value:
            return
        logger.debug('use display %s', self.name)

        if isinstance(value, GeneratorType):
            logger.debug('display generator-type')
            wrapped_generator = wrapper_generator(value)
            is_str = next(wrapped_generator, None)
            if is_str is None:
                return
            if is_str:
                for x in wrapped_generator:
                    self.display_single(action, x, file)
            else:
                self.display(action, list(wrapped_generator), file)
        else:
            # for human-friendly dict type will use display_single
            if isinstance(value, list):
                self.display_many(action, value, file)
            else:
                self.display_single(action, value, file)

    def display_many(self, action: dict, value: Union[dict, list], file: TextIO):
        logger.debug('display-many')

        # 'module': 'primehub.jobs', 'func': 'list'
        customized_key = "{}.{}".format(action['module'], action['func'])
        if customized_key not in CUSTOMIZED_COLUMNS:
            print(tabulate(value, headers="keys"), file=file)
        else:
            def transform(columns: list, v: Union[dict, list]):
                for x in v:
                    result = {}
                    for c in columns:
                        column_name = column_alias = c[0]
                        if len(c) == 2:
                            column_alias = c[1]
                        result[column_alias] = x[column_name]
                    yield result

            print(tabulate(transform(CUSTOMIZED_COLUMNS[customized_key], value), headers="keys"), file=file)

    def display_single(self, action: dict, value: Any, file: TextIO):
        logger.debug('display-single')
        if isinstance(value, str):
            print(value, file=file)
        elif isinstance(value, bytes):
            file.write(value.decode())
        else:
            display_tree_like_format(value, file)
