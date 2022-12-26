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
