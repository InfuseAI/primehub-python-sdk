import importlib
import sys
from argparse import ArgumentParser, Action, RawTextHelpFormatter
from typing import Text, Iterable, Optional

from primehub.utils import create_logger

PhArgGroupClass = getattr(importlib.import_module('argparse'), '_ArgumentGroup')

logger = create_logger('primehub-parser')


class PrimeHubArgParser(ArgumentParser):

    # TODO refine the output message
    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.

        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """

        logger.debug('errors: %s', message)

        # NOTE: we print usage at cli.py module
        # self.print_usage(sys.stderr)
        # args = {'prog': self.prog, 'message': message}
        # self.exit(2, _('%(prog)s: error: %(message)s xx\n') % args)
        # self.exit(1, '\n' + message + '\n\n')
        self.exit(1, '')

    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        if self.description:
            formatter.add_text("  " + self.description)

        if hasattr(self, 'command_description'):
            formatter.add_text(self.command_description)

        action_groups = self._action_groups
        if hasattr(self, 'available_group'):
            action_groups = [self.available_group] + self._action_groups

        # positionals, optionals and user-defined groups
        for action_group in action_groups:
            # hiding original positional arguments
            if action_group.title == 'positional arguments':
                continue
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()

    def add_command_group(self, *args, **kwargs):
        if not hasattr(self, 'available_group'):
            # add dummy command group
            available_group = PhArgGroupClass(ArgumentParser())
            available_group.title = 'Available Commands'
            self.available_group = available_group
        self.available_group.add_argument(*args, **kwargs)


class PrimeHubHelpFormatter(RawTextHelpFormatter):

    def __init__(self,
                 prog,
                 indent_increment=2,
                 max_help_position=24,
                 width=None):
        super(PrimeHubHelpFormatter, self).__init__(prog, indent_increment, max_help_position, width=120)

    def add_usage(self, usage: Text, actions: Iterable[Action], groups: Iterable[PhArgGroupClass],
                  prefix: Optional[Text] = ...) -> None:
        return super(PrimeHubHelpFormatter, self).add_usage(usage, actions, groups, "Usage: \n  ")

    def start_section(self, heading: Optional[Text]) -> None:
        if heading == "optional arguments":
            heading = "Options"
        super(PrimeHubHelpFormatter, self).start_section(heading)


def add_global_options(p):
    help_opts = p.add_argument_group('Options')
    help_opts.add_argument('-h', '--help', help='Show the help', action='store_true', default=False, dest='show_help')
    opts = p.add_argument_group('Global Options')
    opts.add_argument('--config', help='Change the path of the config file (Default: ~/.primehub/config.json)')
    opts.add_argument('--endpoint', help='Override the GraphQL API endpoint')
    opts.add_argument('--token', help='Override the API Token')
    opts.add_argument('--group', help='Override the current group')
    opts.add_argument('--json', help='Output the json format (output human-friendly format by default)',
                      dest='json_output', action='store_true')


def create_command_parser(description=None):
    p = PrimeHubArgParser(formatter_class=PrimeHubHelpFormatter, add_help=False)
    p.add_argument('command')
    p.command_description = description

    add_global_options(p)
    return p


def create_action_parser(group_command, description=None):
    p = PrimeHubArgParser(formatter_class=PrimeHubHelpFormatter, add_help=False)
    p.usage = 'primehub {} <command>'.format(group_command)
    p.add_argument('command')
    p.command_description = description

    return p


if __name__ == '__main__':
    p = create_command_parser()
    p.usage = 'primehub <command>'

    # Add fake commands to the parser's help
    p.add_command_group('config', help='xd')
    p.add_command_group('groups')
    p.print_help(file=sys.stderr)
