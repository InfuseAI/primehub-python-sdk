
# <ADMIN> Primehub Datasets

```
Usage: 
  primehub admin datasets <command>

Manage datasets

Available Commands:
  create               Create a dataset
  delete               Delete a dataset by id
  get                  Get a dataset by name
  list                 Delete a dataset by id
  regen-upload-secret  Regenerate the secret of the upload server
  update               Update the dataset

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### create

Create a dataset


```
primehub admin datasets create
```
 

* *(optional)* file




### delete

Delete a dataset by id


```
primehub admin datasets delete <id>
```

* id: The dataset id
 




### get

Get a dataset by name


```
primehub admin datasets get <name>
```

* name: the name of a dataset
 




### list

Delete a dataset by id


```
primehub admin datasets list
```
 

* *(optional)* page




### regen-upload-secret

Regenerate the secret of the upload server


```
primehub admin datasets regen-upload-secret <id>
```

* id: The dataset id or name
 




### update

Update the dataset


```
primehub admin datasets update <name>
```

* name
 



 

## Examples

### Query datasets

The `datasets` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all datasets in your group:

```
$ primehub admin datasets list
```

```
id           name         displayName                 description                      type
-----------  -----------  --------------------------  -------------------------------  ------
pv-dataset   pv-dataset   the dataset created by SDK  It is a PV dataset               pv
env-dataset  env-dataset  env-dataset                 make changes to the description  env
```

If you already know the name of a dataset, use the `get` to get a single entry:

```
$ primehub admin datasets get dataset
```

```
id:                  pv-dataset
name:                pv-dataset
displayName:         the dataset created by SDK
description:         It is a PV dataset
type:                pv
pvProvisioning:      auto
volumeSize:          1
enableUploadServer:  True
uploadServerLink:    http://primehub-python-sdk.primehub.io/dataset/hub/pv-dataset/browse
global:              False
groups:              [{'id': 'a962305b-c884-4413-9358-ef56373b287c', 'name': 'foobarbar', 'displayName': '', 'writable': False}, {'id': 'a7a283b5-c0e2-4b79-a78c-39c630324762', 'name': 'phusers', 'displayName': 'primehub users', 'writable': False}]
```

### Admin actions for datasets

These actions only can be used by administrators:

* create
* update
* delete

For `create` and `update` require a dataset configuration, please see above examples.

### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| name | required | string | it should be a valid resource name for kubernetes |
| displayName | optional | string | display name for this dataset |
| description | optional | string | |
| global | optional | boolean | when a dataset is global, it could be seen for each group |
| type | required | string | one of ['pv', 'nfs', 'hostPath', 'git', 'env'] |
| url | conditional | string | **MUST** use with `git` type |
| pvProvisioning | conditional | string | onf of ['auto', 'manual'], **MUST** use with `pv` type. This field only uses in `CREATE` action |
| nfsServer | conditional | string | **MUST** use with `nfs` type |
| nfsPath | conditional | string | **MUST** use with `nfs` type |
| hostPath | conditional | string | **MUST** use with `hostPath` type  |
| variables | optional | dict | **MAY** use with `env` type. It is key value pairs. All values have to a string value. For example: `{"key1":"value1","key2":"value2"}`. |
| groups | optional | list of connected groups (dict) | please see the `connect` examples |
| secret | optional | dict | **MAY** use with `git` type, it binds a `secret` to the `git` dataset |
| volumeSize | conditional | integer | **MUST** use with `pv` type. The unit is `GB`.|
| enableUploadServer | optional | boolean | it only works with one of ['pv', 'nfs', 'hostPath'] writable types |

> There is a simple rule to use fields for `UPDATE`. All required fields should not be in the payload.

For example, there is a configuration for creating env dataset:

```bash
primehub datasets create <<EOF
{
  "name": "env-dataset",
  "description": "",
  "type": "env",
  "global": true,
  "variables": {
    "ENV": "prod",
    "LUCKY_NUMBER": "7"
  }
}
EOF
```

After removing required `name` and `type` fields, it could be used with updating:

```bash
primehub admin datasets update env-dataset <<EOF
{
  "description": "make changes to the description",
  "variables": {
    "ENV": "prod",
    "LUCKY_NUMBER": "8"
  }
}
EOF
```


### PV type

```json
{
  "name": "pv-dataset",
  "displayName": "the dataset created by SDK",
  "description": "It is a PV dataset",
  "type": "pv",
  "global": true,
  "pvProvisioning": "auto",
  "volumeSize": 1
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub admin datasets create --file create-dataset.json
```

The example creates a PV dataset. According to the type `pv`, these fields become `required`:
* pvProvisioning: how does the PV create? `auto` means PV will create automatically, `manual` means the system administrator should create it.
* volumeSize: the capacity in GB when `auto` creates it.

The `group.connect` will bind two groups to the dataset. One is a writable group and another is readonly group.


### NFS type

```json
{
  "name": "nfs-dataset",
  "type": "nfs",
  "global": true,
  "nfsServer": "1.2.3.4",
  "nfsPath": "/data"
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub admin datasets create --file create-dataset.json
```

The example creates a NFS dataset. According to the type `nfs`, these fields become `required`:
* nfsServer: the address of a NFS server
* nfsPath: the mount path of a NFS server

### HostPath type

```json
{
  "name": "host-path-dataset",
  "description": "",
  "type": "hostPath",
  "global": true,
  "hostPath": "/opt/data"
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub admin datasets create --file create-dataset.json
```

The example creates a hostPath dataset. According to the type `hostPath`, the `hostPath` field becomes `required`. You should put an absolute path that available in the node.

### Git type

```json
{
  "name": "git-dataset",
  "type": "git",
  "global": true,
  "url": "https://github.com/datasets/covid-19"
}
```

or with a `secret`

```json
{
  "name": "git-dataset",
  "type": "git",
  "global": true,
  "url": "https://github.com/datasets/covid-19",
  "secret": {
    "connect": {
      "id": "gitsync-secret-public-key-for-git-repo"
    }
  }
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub admin datasets create --file create-dataset.json
```

The example creates a git dataset. According to the type `git`, `url` field becomes `required`. You should put a git repository url.

If the url needs a credential, you could use `secret` to connect the pre-set secret (an SSH public key).

### ENV type

```json
{
  "name": "env-dataset",
  "description": "",
  "type": "env",
  "global": true,
  "variables": {
    "ENV": "prod",
    "LUCKY_NUMBER": "7"
  }
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub admin datasets create --file create-dataset.json
```

The example creates an ENV dataset. According to the type `env`, `variables` field becomes `required`. You could put many key-value pairs. Be careful, the key and value should be string values.

### Manage groups in a dataset

In this section, we will discuss the `global` and `groups` fields.

There some use cases to manage groups in a dataset:
* allow any groups to read data 
* allow any groups to read data, but some groups can write
* few groups can read data, some groups can write

etc.

----


Here is an example to create a PV dataset:

```bash
primehub admin datasets create <<EOF
{
  "name": "dataset-with-groups",
  "displayName": "the dataset created by SDK",
  "type": "pv",
  "global": true,
  "groups": {
    "connect": [
      {
        "id": "a7a283b5-c0e2-4b79-a78c-39c630324762",
        "writable": true
      }
    ]
  },
  "pvProvisioning": "auto",
  "volumeSize": 1
}
EOF
```

Please pay attention to `global` and `groups`. When `global` is enabled, it means any groups `can read` the dataset.

> There is not options for global `write`, you have to set the `write` to each group by the `groups.connect` field

#### groups.connect

Here is our example in the `connect`:

```json
{
  "connect": [
    {
      "id": "a7a283b5-c0e2-4b79-a78c-39c630324762",
      "writable": true
    }
  ]
}
```

The `groups.connect` can be used with:

* primehub admin datasets create
* primehub admin datasets update

However, the `writable` only has meanings to `writable` datasets (one of `['pv', 'nfs', 'hostPath']` writable types).
When a writable dataset got a group with `writable: false` setting, it will make the group read-only to the dataset.


#### groups.disconnect

The `groups.disconnect` can be used with:

* primehub admin datasets update


```json
{
  "connect": [
    {
      "id": "a7a283b5-c0e2-4b79-a78c-39c630324762",
      "writable": true
    }
  ],
  "disconnect": [
    {
      "id": "a7a283b5-c0e2-4b79-a78c-39c630324762"
    }
  ]
}
```

`groups.disconnect` will remove the association between the dataset and group.

The result depends on `global` value:
* `true` -> the removed group could read the dataset
* `false` -> the remove group would not see the dataset anymore