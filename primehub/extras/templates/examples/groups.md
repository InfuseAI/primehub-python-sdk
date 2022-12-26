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
