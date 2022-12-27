
# Primehub Groups

```
Usage: 
  primehub groups <command>

Get a group or list groups

Available Commands:
  add-user             Add a user to a group by id
  get                  Get group by name
  get-mlflow           Get MLflow config from a group by id
  list                 List groups
  list-users           List users in the group by id
  remove-user          Remove a user from a group by id
  set-mlflow           Set MLflow config to a group by id
  unset-mlflow         Unset MLflow config from a group by id

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
primehub groups add-user <group_id> <user_id>
```

* group_id: group id
* user_id: user id
 

* *(optional)* is_admin: Add `--is_admin` if the user is added as group admin.




### get

Get group by name


```
primehub groups get <group_name>
```

* group_name: the name of a group
 




### get-mlflow

Get MLflow config from a group by id


```
primehub groups get-mlflow <group_id>
```

* group_id: group id
 




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

Set MLflow config to a group by id


```
primehub groups set-mlflow <group_id>
```

* group_id: group id
 

* *(optional)* file: The file path of MLflow configuration




### unset-mlflow

Unset MLflow config from a group by id


```
primehub groups unset-mlflow <group_id>
```

* group_id: group id
 



 

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

### Group members

List group members of a group by id

```
$ primehub groups list-users daefae90-0fc7-4a5f-ab2c-9a193c461225

id                                    username              firstName    lastName    email                 group_admin
------------------------------------  --------------------  -----------  ----------  --------------------  -------------
9e26cfc4-faba-4aa5-85a8-e8da93eb1a38  foobar                Foo          Bar         hi@infuseai.io        False
```

Add a member to a group by id

```
$ primehub groups add-user daefae90-0fc7-4a5f-ab2c-9a193c461225 4ca09a19-ef14-4800-861f-aec74149a6f4
```
* Add `--is_admin` flag to grant the member group admin permission

Remove a member from a group by id

```
$ primehub groups remove-user daefae90-0fc7-4a5f-ab2c-9a193c461225 4ca09a19-ef14-4800-861f-aec74149a6f4
```

### MLflow configuration

To get MLflow configuration of a group, use `get-mlflow` command:

```
primehub groups get-mlflow <group_id>
```

```
trackingUri:    http://app-mlflow-xyzab:5000
uiUrl:          https://primehub-python-sdk.primehub.io/console/apps/mlflow-xyzab
trackingEnvs:   [{'name': 'NAME1', 'value': 'value1'}]
artifactEnvs:   []
```

To set MLflow configuration, use `set-mlflow` command:

```bash
primehub group set-mlflow <group_id> <<EOF
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
* If `jq` command installed, you can use `jq` to obtain `tracking_uri` easily:
    ```
    primehub apps list --json | jq -r '.[] | select(.appTemplate.id == "mlflow") | {"id": .id, "name": .displayName, "tracking_uri": (.svcEndpoints[0] | tostring | ("http://" + .)) }'
    ```
    ```
    {
      "id": "mlflow-xyzab",
      "name": "mlflow-infuseai",
      "tracking_uri": "http://app-mlflow-xyzab:5000"
    }
    ```

You can also set MLflow configuration from a json file:

```
primehub group set-mlflow <group_id> --file /tmp/mlflow.json
```

To clear MLflow for a group, use `unset-mlflow` command:

```
primehub groups unset-mlflow <group_id>
```