from argparse import ArgumentParser


def default_optional_builder(parser: ArgumentParser, name: str, type_of_arg: type):
    parser.add_argument("--" + name, type=type_of_arg)


def toggle_flag(parser: ArgumentParser, name: str):
    parser.add_argument("--" + name, action="store_true", default=False)


def file_flag(parser: ArgumentParser, name: str):
    if name != 'file':
        raise ValueError(f'name should be file, but it is {name}')
    parser.add_argument("--file", "-f", dest='file')
