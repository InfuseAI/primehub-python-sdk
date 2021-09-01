import sys
import traceback

import primehub as ph
from primehub.config import CliConfig
from primehub.utils import create_logger, PrimeHubException, PrimeHubReturnsRequiredException, ResourceNotFoundException
from primehub.utils.argparser import create_command_parser, create_action_parser
from primehub.utils.decorators import find_actions, find_action_method, find_action_info
from primehub.utils.permission import has_permission_flag, enable_ask_for_permission_feature

logger = create_logger('primehub-cli')


def attach_dev_lab(p):
    import os
    if 'true' == os.environ.get('PRIMEHUB_SDK_DEVLAB', 'false'):
        p.register_command('extras.devlab', 'DevLab', 'devlab')
        p.register_command('extras.e2e', 'E2EForBasicFunction', 'e2e')


def create_sdk():
    cfg = ph.PrimeHubConfig()
    sdk = ph.PrimeHub(cfg)
    # Note: We replace the config to CliConfig, please see details at config module
    sdk.register_command('config', 'CliConfig')
    sdk.register_command('info', 'CliInformation')

    attach_dev_lab(sdk)
    return sdk


def reconfigure_group(sdk):
    config_command: CliConfig = sdk.config
    config_command.reconfigure_group(sdk.primehub_config.group)


def create_commands(parser, sdk):
    parsers = dict()

    for command_group in sorted(sdk.commands.keys()):
        target = sdk.commands[command_group]

        # Add the action to the main parser
        parser.add_command_group(command_group, help=target.help_description())

        # Create the group parser
        p = parsers[command_group] = create_command_parser(description=target.help_description())
        p.usage = """primehub {} <command>""".format(command_group)

        for action in find_actions(target):
            name, description = action['name'], action['description']
            p.add_command_group(name, help=description)

    return parsers


def run_action_args(sdk, selected_component, sub_parsers, target, remaining_args):
    logger.debug('invoke {} with remaining_args: {}'.format(run_action_args.__name__, remaining_args))
    helper = None

    # validate the user input command and parameters
    # primehub [command]             [unchecked params]
    #          selected_component    remaining_args
    #          sub_args.command      [params]
    #                                [action] + [params]
    sub_args, params = sub_parsers[selected_component].parse_known_args(remaining_args)
    logger.debug('sub_args: {}, params: {}'.format(sub_args, params))

    try:
        action = find_action_info(target, sub_args.command)
        if not action:
            helper = sub_parsers[selected_component]
            return helper

        # build a parser for selected action
        # primehub [command]             [action] [param1] [param2] ...
        action_parser = create_action_parser(selected_component)

        # Note: DONT add-command-group for action command
        # action_parser.add_command_group(sub_args.command, help=action['description'])
        argument_names = []
        has_kwargs = False
        logger.debug('create the action parser: {}'.format(action))
        for x in action['arguments']:
            param_name, param_type, skip_if_kwargs = x
            if skip_if_kwargs:
                # we will add optional argument in the next step
                # convert it to `--<arg-name>` format
                has_kwargs = True
                continue
            action_parser.add_argument(param_name, type=param_type)
            argument_names.append(param_name)

        # @cmd with optionals
        for x in action['optionals']:
            # There is a tuple (x, y, z, ..., arg_builder) for each optional
            # We use the arg_builder to create a new argument
            arg_builder = x[-1]
            arg_builder_args = [action_parser] + list(x[0:-1])
            arg_builder(*arg_builder_args)

        # @ask_for_permission
        if has_permission_flag(action):
            action_parser.add_argument('--yes-i-really-mean-it', dest='__primehub_permission__', action="store_true")

        action_parser.usage = 'primehub {} {} {}'.format(
            selected_component, sub_args.command, " ".join(["<%s>" % x for x in argument_names]))

        if sub_args.show_help:
            logger.debug('skip doing action, because of help calling')
            helper = action_parser
            return helper

        try:
            parsed_action_args = action_parser.parse_args([sub_args.command] + params)
            logger.debug('parsed_action_args: %s', parsed_action_args)

            # invoke <command_group>.<action>(param1, param2, ...) from the register command
            action_func = action['func']
            logger.debug('find action: {}, for target: {}'.format(action_func, target))
            func = getattr(target, action_func)

            real_parameters = []
            for x in argument_names:
                real_parameters.append(getattr(parsed_action_args, x))

            kw_parameters = {}
            if has_kwargs:
                for x in action['optionals']:
                    opt_name = x[0]
                    v = getattr(parsed_action_args, opt_name)
                    if v is not None:
                        kw_parameters[opt_name] = v

            if has_kwargs:
                if hasattr(parsed_action_args,
                           '__primehub_permission__') and parsed_action_args.__primehub_permission__:
                    kw_parameters['--yes-i-really-mean-it'] = True
                logger.debug('invoke with parameters %s {%s}', real_parameters, vars(parsed_action_args))
                return_value = func(*real_parameters, **kw_parameters)
            else:
                logger.debug('invoke with parameters %s', real_parameters)
                return_value = func(*real_parameters)
            if return_value:
                display_func = getattr(target, 'display')
                display_func(action, return_value)
            else:
                if action['return_required']:
                    raise PrimeHubReturnsRequiredException()
        except SystemExit:
            return action_parser

    except AttributeError:
        logger.debug('{}'.format(sys.exc_info()))
        traceback.print_tb(tb=sys.exc_info()[-1])
        helper = sub_parsers[selected_component]
    return helper


def run_action_noargs(sdk, selected_component, sub_parsers, target, args):
    logger.debug('invoke %s', run_action_noargs.__name__)
    helper = None
    try:
        if args.show_help:
            helper = sub_parsers[selected_component]
            return helper

        action = find_action_method(target, args.command)
        logger.debug('remaining_args is empty, find an action from parent\'s command [{}] => method: {}'
                     .format(args.command, action))
        if action is None:
            helper = sub_parsers[selected_component]
            logger.debug('cannot find a handler for %s! stop and print the help', args.command)
            return helper

        # invoke <command_group>.<action>() from the register command
        func = getattr(target, action)
        return_value = func()
        logger.debug('invoked {}'.format(func))
        if return_value:
            display_func = getattr(target, 'display')
            display_func(action, return_value)
        else:
            if action['return_required']:
                raise PrimeHubReturnsRequiredException()
    except AttributeError:
        logger.debug('{}'.format(sys.exc_info()))
        helper = sub_parsers[selected_component]
    return helper


def main(sdk=None):
    main_parser = create_command_parser()
    main_parser.usage = """primehub <command>"""

    if not sdk:
        sdk = create_sdk()

    # enable @ask_for_permission for command-line
    enable_ask_for_permission_feature()

    command_groups = create_commands(main_parser, sdk)

    hide_help = False
    helper = None
    exit_normally = False
    try:
        logger.debug('start to parse {}'.format(sys.argv))
        args, remaining_args = main_parser.parse_known_args()
        command_name = args.command
        logger.debug("args: {}".format(args))
        logger.debug("remaining_args: {}".format(remaining_args))
        reconfigure_primehub_config_if_needed(args, sdk)

        # configure output format from main-parser
        sdk.json_output = args.json_output

        if command_name not in sdk.commands:
            main_parser.epilog = 'Error: "{}" command not found'.format(command_name)
            sys.exit(1)

        # the real object to execute command
        target = sdk.commands[command_name]
        logger.debug("component: {}, target: {}".format(command_name, target))

        # got show-help, print help and exit normally
        if args.show_help and not remaining_args:
            helper = command_groups[command_name]
            exit_normally = True
            sys.exit(0)

        if args.show_help and remaining_args:
            remaining_args.append('-h')

        if remaining_args:
            helper = run_action_args(sdk, command_name, command_groups, target, remaining_args)
        else:
            helper = run_action_noargs(sdk, command_name, command_groups, target, args)

        if helper:
            sys.exit(1)

    except PrimeHubReturnsRequiredException:
        logger.debug('got PrimeHubReturnsRequiredException')
        hide_help = True
        exit_normally = False
        sys.exit(1)
    except ResourceNotFoundException as e:
        logger.debug('got PrimeHubReturnsRequiredException')
        hide_help = True
        exit_normally = False
        type_name, key, key_type = e.args
        print(f'Cannot find resource type "{type_name}" with [{key_type}: {key}]', file=sdk.stderr)
        sys.exit(1)
    except PrimeHubException as e:
        hide_help = True
        exit_normally = False
        print(e, file=sdk.stderr)
        sys.exit(1)
    except SystemExit:
        if not hide_help:
            if helper:
                helper.print_help(file=sdk.stderr)
            else:
                main_parser.print_help(file=sdk.stderr)

        if exit_normally:
            sys.exit(0)
        else:
            sys.exit(1)

    # exit application normally
    sys.exit(0)


def reconfigure_primehub_config_if_needed(args, sdk):
    if args.config is not None or args.endpoint is not None or args.group is not None or args.token is not None:
        sdk.primehub_config = ph.PrimeHubConfig(
            config=args.config, endpoint=args.endpoint,
            group=args.group, token=args.token)
        reconfigure_group(sdk)


if __name__ == '__main__':
    main()
