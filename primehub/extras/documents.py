import io
import os
import sys

from primehub.utils.decorators import find_actions

from primehub import PrimeHub

from primehub.cli import create_sdk, main as cli_main
from primehub.utils.permission import has_permission_flag

markdown_template = """

# Primehub %(command_capitalized)s

primehub %(command)s `<verb>` `[args]` `[flags]`



## Available Commands

%(command_list)s
"""

action_template = """
#### %(action_capitalized)s

%(description)s %(require_permission)s

```
primehub %(group)s %(action)s %(arg_list)s
```
"""


def get_doc_path():
    import primehub

    p = os.path.abspath(os.path.dirname(primehub.__file__) + "/../docs")
    return p


def create_cli_doc_path(name):
    doc_path = os.path.join(get_doc_path(), 'CLI', name + ".md")
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    return doc_path


def generate_help_for_command(sdk: PrimeHub, name):
    sdk.stderr = io.StringIO()
    sdk.stdout = io.StringIO()
    sys.argv = ['primehub', name, '-h']
    try:
        cli_main(sdk=sdk)
    except SystemExit:
        pass
    command_help = sdk.stderr.getvalue()
    print("generate command-group:", name)

    command_list = "\n".join(["- %s" % x['name'] for x in find_actions(sdk.commands[name])])

    action_docs = []
    for action in find_actions(sdk.commands[name]):
        print(action)
        print("generate action:", action['name'])
        require_permission = ""
        if has_permission_flag(action):
            require_permission = "(`--yes-i-really-mean-it` is required)"
        arg_list = " ".join(["<%s>" % x[0] for x in action['arguments'] if not x[2]])
        text = action_template % dict(group=name, action_capitalized=action['name'].capitalize(),
                                      action=action['name'],
                                      description=action['description'], require_permission=require_permission,
                                      arg_list=arg_list)

        action_docs.append(text)

    p = create_cli_doc_path(name)
    with open(p, "w") as fh:
        content = markdown_template % dict(command_capitalized=name.capitalize(), command=name,
                                           help=command_help.strip(), command_list=command_list)
        fh.write(content)
        fh.write("\n")
        fh.write("\n".join(action_docs))
        fh.write("\n")
        fh.write("## Help")
        fh.write("""
```
%s
```
        """ % command_help.strip())


def main():
    sdk = create_sdk()
    for k, v in sdk.commands.items():
        if k == 'devlab':
            continue
        generate_help_for_command(sdk, k)


if __name__ == '__main__':
    main()
