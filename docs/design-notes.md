# Design: PrimeHub Python SDK

Objective

- Ship the PrimeHub Python SDK and CLI together

Key Results →

- CLI is derived from the SDK
    - needn't rework CLI after the SDK shipped
    - generate documentation from the source code
- friendly collaboration
    - pluggable structure makes programmers working without conflicts

## Core Types

- PrimeHubConfig represents the SDK configuration file.
- PrimeHub serves
    - the plug-in registry
    - command builder
        - inject HTTP-Clients (with authorization token)
            - request: GraphQL Post
            - request_logs: logs `generator`
            - request_files: shared files downloader
        - export required config values
- python decorator
    - `@cmd`: export SDK method to CLI
    - `@ask_for_permission`: ask for permission before a dangerous action has executed

## Build a Command

- Steps
    - create a command group
    - define actions in a command group and expose action by `@cmd` decorator
    - register the command group to the PrimeHub

We put command groups in `primehub` package

```bash
primehub
├── __init__.py
├── cli.py
├── config.py
├── volumes.py
├── files.py
├── group.py
├── images.py
├── info.py
├── instancetypes.py
├── jobs.py
├── me.py
├── notebooks.py
├── resource_operations.py
└── schedules.py
```

### Create a command group

We use `me` command group as the example.

- create a `me.py` in the primehub package
    - extends `Helpful` class
        - implement the help description to CLI
    - extends `Module` class
        - connect the `PrimeHub` instance to the command group
            - get config values
            - call other plugin
        - attach http clients

```python
from primehub import Helpful, cmd, Module

class Me(Helpful, Module):

    def help_description(self):
        return "Show user account"
```

### Define an action and expose it to the command line

- `me` method is the command action, it executes whatever you want.
    - it `request`s to the GraphQL
        - the first arg is `variables` to the query
        - the second arg is the query
- expose to CLI by the `@cmd`

```python
from primehub import Helpful, cmd, Module

class Me(Helpful, Module):

    @cmd(name='me', description='Get user information')
    def me(self) -> dict:
        """
        Get account information

        :rtype: dict
        :returns: account information
        """
        query = """
        query {
          me {
            id
            username
            firstName
            lastName
            email
            isAdmin
          }
        }
        """
        result = self.request({}, query)
        if 'data' in result and 'me' in result['data']:
            return result['data']['me']
        return result

    def help_description(self):
        return "Show user account"
```

You could see the output with `-h`

```bash
$ primehub me -h
Usage:
  primehub me <command>

Show user account

Available Commands:
  me                   Get user information

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group
```

### Register command to PrimeHub

All commands are registered when a PrimeHub object initialization. Please update the `__init__` adding this line:

```python

# arg 1: a python file in the primehub/me.py
# arg 2: the command group class in the my.py
self.register_command('me', 'Me')
```

```python
class PrimeHub(object):

    def __init__(self, config: PrimeHubConfig):
        self.primehub_config = config
        self.commands: Dict[str, Module] = dict()
        self._stderr = sys.stderr
        self._stdout = sys.stdout

        # register commands
        self.register_command('config', 'Config')
        self.register_command('group', 'Group')
        self.register_command('images', 'Images')
        self.register_command('volumes', 'Volumes')
        self.register_command('instancetypes', 'InstanceTypes')
        self.register_command('jobs', 'Jobs')
        self.register_command('schedules', 'Schedules')
        self.register_command('notebooks', 'Notebooks')
        self.register_command('files', 'Files')
        self.register_command('me', 'Me')

        # initial
        self._ensure_config_details(config)
```

## SDK to CLI showcases

Please check the `FakeCommand` in the test cases

[https://github.com/InfuseAI/primehub-python-sdk/blob/main/tests/test_sdk_to_cli.py](https://github.com/InfuseAI/primehub-python-sdk/blob/main/tests/test_sdk_to_cli.py#L9)
