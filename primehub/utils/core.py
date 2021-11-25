import random
import re
from collections import UserDict


class CommandContainer(UserDict):

    def keys(self):
        return [x for x in super(CommandContainer, self).keys() if not x.startswith(':')]

    def items(self):
        return [(k, v) for (k, v) in super(CommandContainer, self).items() if not k.startswith(':')]

    def __getitem__(self, item):
        try:
            return super(CommandContainer, self).__getitem__(item)
        except KeyError:
            return super(CommandContainer, self).__getitem__(f':{item}')

    def __contains__(self, item):
        has_item = super(CommandContainer, self).__contains__(item)
        if has_item:
            return True
        return super(CommandContainer, self).__contains__(f':{item}')


def auto_gen_id(name: str):
    normalized_name = re.sub(r'[\W_]', '-', name).lower()
    random_string = str(float.hex(random.random()))[4:9]
    return f'{normalized_name}-{random_string}'
