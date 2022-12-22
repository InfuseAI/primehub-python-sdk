
# Primehub Groups

```
Usage: 
  primehub groups <command>

Get a group or list groups

Available Commands:
  add-user             Add a user to a group by id
  get                  Get group by name
  get-mlflow           Get MLflow config from current group
  list                 List groups
  list-users           List users in the group by id
  remove-user          Remove a user from a group by id
  set-mlflow           Set MLflow config to current group
  unset-mlflow         Unset MLflow config from current group

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### add-user

Add a user to a group by id


```
primehub groups add-user <group_id> <user_id> <is_admin>
```

* group_id: group id
* user_id: user id
* is_admin: 'True' if the user is added as group admin, and 'False' otherwise, defaults to False
 




### get

Get group by name


```
primehub groups get <group_name>
```

* group_name: the name of a group
 




### get-mlflow

Get MLflow config from current group


```
primehub groups get-mlflow
```
 




### list

List groups


```
primehub groups list
```
 




### list-users

List users in the group by id


```
primehub groups list-users <group_id>
```

* group_id: group id
 




### remove-user

Remove a user from a group by id


```
primehub groups remove-user <group_id> <user_id>
```

* group_id: group id
* user_id: user id
 




### set-mlflow

Set MLflow config to current group


```
primehub groups set-mlflow
```
 

* *(optional)* file: The file path of MLflow configuration




### unset-mlflow

Unset MLflow config from current group


```
primehub groups unset-mlflow
```
 



 

## Examples

`groups` command can show the available groups for your account.

If you have the name of a group, `get` will be useful:

```
primehub groups get phusers
```

The `list` command will show any groups your account belongs to:

```
primehub groups list
```

```
id                                    name     displayName     quotaCpu      quotaGpu  quotaMemory    projectQuotaCpu      projectQuotaGpu  projectQuotaMemory
------------------------------------  -------  --------------  ----------  ----------  -------------  -----------------  -----------------  --------------------
2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376  phusers  primehub users                       0                                                    0
```

### MLflow configuration

To get MLflow configuration of current group, use `get-mlflow` command:

```
primehub groups get-mlflow
```

```
trackingUri:    http://app-mlflow-xyzab:5000
uiUrl:          https://primehub-python-sdk.primehub.io/console/apps/mlflow-xyzab
trackingEnvs:   [{'name': 'NAME1', 'value': 'value1'}]
artifactEnvs:   []
```

To set MLflow configuration, use `set-mlflow` command:

```bash
primehub group set-mlflow <<EOF
{
  "tracking_uri": "http://app-mlflow-xyzab:5000",
  "ui_uri": "https://primehub-python-sdk.primehub.io/console/apps/mlflow-xyzab",
  "artifactEnvs": [
    { "name": "NAME1", "value": "value1" },
    { "name": "NAME2", "value": "value2" }
  ]
}
EOF
```

* The `tracking_uri` field is required for `set-mlflow` command

You can also set MLflow configuration from a json file:

```
primehub group set-mlflow --file /tmp/mlflow.json
```

To clear MLflow for current group, use `unset-mlflow` command:

```
primehub groups unset-mlflow
```