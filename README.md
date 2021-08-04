# PrimeHub Python SDK

PrimeHub Python SDK provides a python library to communicate with PrimeHub API

## Installation

Install the SDK from source code

```
git clone https://github.com/InfuseAI/primehub-python-sdk.git
cd primehub-python-sdk
pip install -e .[dev]
```

Verify it with `primehub` command:

```bash
Usage:
  primehub <command>

Available Commands:
  config               Update the settings of PrimeHub SDK
  datasets             Get a dataset or list datasets
  files                List and download shared files
  group                Get a group or list groups
  images               Get a image or list images
  info                 Display the user information and the selected group information
  instancetypes        Get an instance types of list instance types
  jobs                 Get a job or list jobs
  me                   Show user account
  notebooks            Get notebooks logs
  schedules            Get a schedule or list schedules

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group
```

## Configuration

PrimeHub Python SDK needs the `~/.primehub/config.json` to connect to your PrimeHub API server.

```json
{
  "api-token": "<api-token>",
  "endpoint": "https://<primehub-server-domain>/api/graphql",
  "group": {
    "name": "<the-name-of-current-group>"
  }
}
```

* api-token and endpoint: please generate your own api-token and get the endpoint from the PrimeHub Console
* group: the name of a group. If the SDK did a group-context aware query, the group name would be used. It would raise an exception when the group was not available.

The configuration could verify by `me`：

```
$ primehub me | jq .
{
  "id": "a932f38d-cca7-4846-5566-b2958949e7c9",
  "username": "jovyan",
  "firstName": "",
  "lastName": "",
  "email": "jovyan@infuseai.io,
  "isAdmin": true
}
```