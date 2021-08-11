import json
from types import GeneratorType
from typing import Any, TextIO, Union

from primehub import create_logger

logger = create_logger('display')


def wrapper_generator(gen):
    is_type_sent = False
    for x in gen:
        if not is_type_sent:
            yield isinstance(x, str)
            is_type_sent = True
        yield x


class Display(object):

    def __init__(self, name: str):
        self.name = name

    def display(self, action: dict, value: Any, file: TextIO):
        if not value:
            return

        if isinstance(value, GeneratorType):
            logger.debug('display generator-type')
            wrapped_generator = wrapper_generator(value)
            is_str = next(wrapped_generator, None)
            if is_str is None:
                return
            if is_str:
                for x in wrapped_generator:
                    self.display_single(x, file)
            else:
                self.display(action, list(wrapped_generator), file)
        else:
            if isinstance(value, dict) or isinstance(value, list):
                self.display_many(value, file)
            else:
                self.display_single(value, file)

    def display_many(self, value: Union[dict, list], file: TextIO):
        logger.debug('display-many')
        json.dump(value, file)

    def display_single(self, value: Any, file: TextIO):
        logger.debug('display-single')
        if isinstance(value, str):
            print(value, file=file)
        else:
            json.dump(value, file)
