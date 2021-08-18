import io
import os
import re
import sys

from jinja2 import Environment, PackageLoader, select_autoescape

from primehub import PrimeHub
from primehub.cli import create_sdk, main as cli_main
from primehub.utils.decorators import find_actions, find_action_method

env = Environment(
    loader=PackageLoader("primehub.extras"),
    autoescape=select_autoescape()
)


def get_example(command):
    try:
        return env.get_template('examples/{}.md'.format(command)).render()
    except BaseException:
        pass
    return "TBD: please write example for [{}]".format(command)


def get_doc_path():
    import primehub

    p = os.path.abspath(os.path.dirname(primehub.__file__) + "/../docs")
    return p


def create_cli_doc_path(name):
    doc_path = os.path.join(get_doc_path(), 'CLI', name + ".md")
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    return doc_path


def generate_command_document(*args, **kwargs):
    return env.get_template('cli.tpl.md').render(*args, **kwargs)


def generate_help_for_command(sdk: PrimeHub, name):
    sdk.stderr = io.StringIO()
    sdk.stdout = io.StringIO()
    sys.argv = ['primehub', name, '-h']
    try:
        cli_main(sdk=sdk)
    except SystemExit:
        pass
    command_help = sdk.stderr.getvalue()
    actions = find_actions(sdk.commands[name])
    attach_template_information_to_action(actions, name, sdk)
    document = generate_command_document(command=name, command_help=command_help,
                                         actions=actions, examples=get_example(name))

    print("Generate doc", name)
    p = create_cli_doc_path(name)
    with open(p, "w") as fh:
        fh.write(document)


def attach_template_information_to_action(actions, name, sdk):
    for action in actions:
        explain = extract_description_from_docstring(action, name, sdk)

        def explained(x):
            if x in explain:
                return "{}: {}".format(x, explain[x])
            return x

        # arguments
        arg_list = []
        for x in action['arguments']:
            if x[2] is True:
                # skip **kwargs
                continue
            arg_list.append(x[0])
        action['required_arguments_string'] = " ".join(["<%s>" % x for x in arg_list])
        action['required_arguments'] = [explained(x) for x in arg_list]

        # optionals
        opt_list = []
        for x in action['optionals']:
            opt_list.append(x[0])
        action['optional_arguments'] = [explained(x) for x in opt_list]


def extract_description_from_docstring(action, name, sdk):
    output = dict()
    method_name = find_action_method(sdk.commands[name], action['name'])
    doc_string = getattr(sdk.commands[name], method_name).__doc__
    param_description = re.findall(r':param ([^:]+):(.+)', str(doc_string))
    for k, v in param_description:
        output[k.strip()] = v.strip()
    return output


def main():
    sdk = create_sdk()
    for k, v in sdk.commands.items():
        if k == 'devlab':
            continue
        if k == 'version':
            continue
        generate_help_for_command(sdk, k)


if __name__ == '__main__':
    main()
