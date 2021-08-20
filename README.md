# PrimeHub Python SDK

PrimeHub Python SDK is the PrimeHub AI Platform Software Development Kit (SDK) for Python, which allows Python
developers to write software that makes use of services like Job and Deployment.

## Getting Started

Assuming that you have Python, you can install the library using pip:

```
$ pip install primehub-python-sdk
```

## Using CLI

After installing PrimeHub Python SDK

Next, set up the configuration in `~/.primehub/config.json`:

```json
{
  "api-token": "<api-token>",
  "endpoint": "https://<primehub-domain>/api/graphql",
  "group": {
    "name": "<group-name>"
  }
}
```

The `<api-token>` could [be generated from User Portal](https://docs.primehub.io/docs/tasks/api-token).

Then, from a shell:

```
$ primehub me
id:             a7db12dc-04fa-419c-9cd7-af768575a871
username:       phadmin
firstName:      None
lastName:       None
email:          dev+phadmin@infuseai.io
isAdmin:        True
```

Running `primehub` without arguments to show help:

```
$ primehub
Usage:
  primehub <command>

Available Commands:
  config               Update the settings of PrimeHub SDK
  datasets             Get a dataset or list datasets
  deployments          Get a deployment or list deployments
  files                List and download shared files
  groups               Get a group or list groups
  images               Get a image or list images
  info                 Display the user information and the selected group information
  instancetypes        Get an instance types of list instance types
  jobs                 Get a job or list jobs
  me                   Show user account
  notebooks            Get notebooks logs
  schedules            Get a schedule or list schedules
  version              Display the version of PrimeHub Python SDK

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)
```

## SDK

from a Python interpreter:

```
In [1]: from primehub import PrimeHub, PrimeHubConfig

In [2]: ph = PrimeHub(PrimeHubConfig())

In [3]: ph.me.me()
Out[3]:
{'id': 'a7db12dc-04fa-419c-9cd7-af768575a871',
 'username': 'phadmin',
 'firstName': None,
 'lastName': None,
 'email': 'dev+phadmin@infuseai.io',
 'isAdmin': True}

In [4]:
```

## Docs

There is a [docs](https://github.com/InfuseAI/primehub-python-sdk/tree/main/docs) folder in our repository. You could find:

* [CLI](https://github.com/InfuseAI/primehub-python-sdk/tree/main/docs/CLI): all commands usage examples
* [notebook](https://github.com/InfuseAI/primehub-python-sdk/tree/main/docs/notebook): examples written in python