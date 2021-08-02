import io
import os
import re
import sys

from jinja2 import Environment, PackageLoader, select_autoescape

from primehub import PrimeHub
from primehub.cli import create_sdk, main as cli_main
from primehub.utils.decorators import find_actions, find_action_method, find_action_info

env = Environment(
    loader=PackageLoader("primehub.extras"),
    autoescape=select_autoescape()
)


def get_doc_path():
    import primehub

    p = os.path.abspath(os.path.dirname(primehub.__file__) + "/../docs")
    return p


def create_cli_doc_path(name):
    doc_path = os.path.join(get_doc_path(), 'CLI', name + ".md")
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    return doc_path


def generate_command_document(*args, **kwargs):
    return env.get_template('command_line.template.md.j2').render(*args, **kwargs)


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
    for action in actions:

        explain = extract_description_from_docstring(action, name, sdk)

        def explained(x):
            if x in explain:
                return "{}: {}".format(x, explain[x])
            return x

        ## arguments
        arg_list = []
        for x in action['arguments']:
            if x[2] is True:
                # skip **kwargs
                continue
            arg_list.append(x[0])
        action['required_arguments_string'] = " ".join(["<%s>" % x for x in arg_list])
        action['required_arguments'] = [explained(x) for x in arg_list]

        ## optionals
        opt_list = []
        for x in action['optionals']:
            opt_list.append(x[0])
        action['optional_arguments'] = [explained(x) for x in opt_list]
    document = generate_command_document(command=name, command_help=command_help,
                                         actions=actions)

    p = create_cli_doc_path(name)
    with open(p, "w") as fh:
        fh.write(document)
    # print("generate command-group:", name)


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
        generate_help_for_command(sdk, k)


if __name__ == '__main__':
    # print(env.get_template('command_line.template.md.j2'))
    main()
