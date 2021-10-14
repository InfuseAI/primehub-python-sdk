
# Primehub Datasets

```
Usage: 
  primehub datasets <command>

Get a dataset or list datasets

Available Commands:
  get                  Get a dataset by name
  list                 List datasets

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### get

Get a dataset by name


```
primehub datasets get <name>
```

* name: the name of a dataset
 




### list

List datasets


```
primehub datasets list
```
 



 

## Examples

### Query datasets

The `datasets` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all datasets in your group:

```
$ primehub datasets list
```

```
id           name         displayName                 description                      type
-----------  -----------  --------------------------  -------------------------------  ------
pv-dataset   pv-dataset   the dataset created by SDK  It is a PV dataset               pv
env-dataset  env-dataset  env-dataset                 make changes to the description  env
```

If you already know the name of a dataset, use the `get` to get a single entry:

```
$ primehub datasets get dataset
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
| secret | optional | dict | **MAY** use with `git` type | bind a `secret` to the `git` dataset |
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
  "variables": {
    "ENV": "prod",
    "LUCKY_NUMBER": "7"
  }
}
EOF
```

After removing required `name` and `type` fields, it could be used with updating:

```bash
primehub datasets update env-dataset <<EOF
{
  "description": "make changes to the description",
  "variables": {
    "ENV": "prod",
    "LUCKY_NUMBER": "8"
  }
}
EOF
```

For updating, giving things that you want to make different:

```bash
primehub datasets update env-dataset <<EOF
{
    "groups": {
      "connect": [
        {
          "id": "a7a283b5-c0e2-4b79-a78c-39c630324762",
          "writable": false
        }
      ]
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
  "global": false,
  "groups": {
    "connect": [
      {
        "id": "a7a283b5-c0e2-4b79-a78c-39c630324762",
        "writable": true
      },
      {
        "id": "a962305b-c884-4413-9358-ef56373b287c",
        "writable": false
      }
    ]
  },
  "pvProvisioning": "auto",
  "volumeSize": 1
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub datasets create --file create-dataset.json
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
  "groups": {
    "connect": [
      {
        "id": "a7a283b5-c0e2-4b79-a78c-39c630324762",
        "writable": true
      }
    ]
  },
  "nfsServer": "1.2.3.4",
  "nfsPath": "/data"
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub datasets create --file create-dataset.json
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
  "groups": {
    "connect": [
      {
        "id": "a7a283b5-c0e2-4b79-a78c-39c630324762",
        "writable": true
      }
    ]
  },
  "hostPath": "/opt/data"
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub datasets create --file create-dataset.json
```

The example creates a hostPath dataset. According to the type `hostPath`, the `hostPath` field becomes `required`. You should put an absolute path that available in the node.

### Git type

```json
{
  "name": "git-dataset",
  "type": "git",
  "url": "https://github.com/datasets/covid-19"
}
```

or with a `secret`

```json
{
  "name": "git-dataset",
  "type": "git",
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
primehub datasets create --file create-dataset.json
```

The example creates a git dataset. According to the type `git`, `url` field becomes `required`. You should put a git repository url.

If the url needs a credential, you could use `secret` to connect the pre-set secret (an SSH public key).

### ENV type

```json
{
  "name": "env-dataset",
  "description": "",
  "type": "env",
  "variables": {
    "ENV": "prod",
    "LUCKY_NUMBER": "7"
  }
}
```

Save the configuration to `create-dataset.json` and run `create`:

```
primehub datasets create --file create-dataset.json
```

The example creates an ENV dataset. According to the type `env`, `variables` field becomes `required`. You could put many key-value pairs. Be careful, the key and value should be string values.

### Group connect/disconnect

All dataset types could connect or disconnect to groups, but there is subtle difference between `CREATE` and `UPDATE`.

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

* `disconnect` is only available for `UPDATE`
* `connect` are both available (`CREATE` `UPDATE`)