from argparse import ArgumentParser


def default_optional_builder(parser: ArgumentParser, name: str, type_of_arg: type):
    parser.add_argument("--" + name, type=type_of_arg)


def toggle_flag(parser: ArgumentParser, name: str):
    parser.add_argument("--" + name, action="store_true", default=False)
