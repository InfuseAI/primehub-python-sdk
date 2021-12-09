import os
from ..cli import create_sdk
from .decorators import find_actions

variables = ('COMP_CWORD', 'COMP_LINE', 'COMP_POINT', 'COMP_WORDS', 'cur', 'prev')

sdk = create_sdk()

PRIMEHUB_AUTO_COMPLETION_LOG = (os.environ.get('PRIMEHUB_AUTO_COMPLETION_LOG', 'false') == 'true')


def _debug_log(x):
    if not PRIMEHUB_AUTO_COMPLETION_LOG:
        return
    with open('.auto-primehub.txt', 'a') as fh:
        fh.write(x)
        fh.write('\n')


def _debug_variables():
    if not PRIMEHUB_AUTO_COMPLETION_LOG:
        return
    with open('.auto-primehub.txt', 'a') as fh:
        fh.write('-' * 16)
        fh.write('\n')
        for v in variables:
            fh.write(f'{v}={os.environ.get(v)}\n')


def auto_complete():
    _debug_variables()

    # first level command groups
    # primehub <auto-completion>
    # cur = os.environ.get('cur')
    prev = os.environ.get('prev')
    current_index = os.environ.get('COMP_CWORD')
    if prev == 'primehub':
        for k in sdk.commands:
            if k.startswith(':'):
                continue
            print(k)
        return

    # primehub <current-group> <auto-completion>
    if current_index == '2':
        _debug_log(f'{prev} => {sdk.commands.keys()}')
        if prev in sdk.commands:
            for verb in find_actions(sdk.commands[prev]):
                print(verb['name'])
        pass


if __name__ == '__main__':
    auto_complete()
