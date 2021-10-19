
# <ADMIN> Primehub Instancetypes

```
Usage: 
  primehub admin instancetypes <command>

Manage instance type

Available Commands:
  create               Create an instance type
  delete               Delete an instance type by id
  get                  Get an instance type by id
  list                 List instance type
  update               Update the instance type

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

Create an instance type


```
primehub admin instancetypes create
```
 

* *(optional)* file: The file path of the configurations

* *(optional)* from




### delete

Delete an instance type by id


```
primehub admin instancetypes delete <id>
```

* id: the id of an instance type
 




### get

Get an instance type by id


```
primehub admin instancetypes get <id>
```

* id: the id of an instance type
 




### list

List instance type


```
primehub admin instancetypes list
```
 

* *(optional)* page: the page of all data




### update

Update the instance type


```
primehub admin instancetypes update <id>
```

* id: the id of the instance type
 

* *(optional)* file



 

## Examples

### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| name | required | string | it should be a valid resource name for kubernetes. `name` will be ignored when updating |
| displayName | optional | string | display name for the instance type |
| description | optional | string | |
| global | optional | boolean | when an instance type is global, it could be seen for each group |
| groups | optional | list of connected groups (dict) | please see the `connect` examples |
| cpuLimit | required | float | the maximum vCPU quantity. For example: `1` or `1.0` means 1 vCPU and `0.5` means half of vCPU |
| cpuRequest | optional | float | the initial vCPU quantity for CPU resource. cpuRequest can not be greater than cpuLimit |
| memoryLimit | required | float | the maximum Memory size. For example: `1.5` means `1.5 GB` memory |
| memoryRequest | optional | float | the initial Memory size. memoryRequest can not be greater than memoryLimit |
| gpuLimit | optional | int | the count of GPU when an instance allocated |
| tolerations | optional | dict | kubernetes pod toleration in an instance (Pod) |
| nodeSelector | optional | dict | kubernetes pod nodeSelector in an instance (Pod) |

### Create an instance type

By convention, creating without valid inputs will show an example:

```
$ primehub admin instancetypes create

The configuration is required.

Example:
{
  "name": "cpu-1",
  "displayName": "CPU 1",
  "description": "1 vCPU / 1G Memory",
  "cpuLimit": 1,
  "memoryLimit": 1,
  "gpuLimit": 0,
  "global": true,
  "tolerations": {
    "set": [
      {
        "operator": "Equal",
        "effect": "NoSchedule",
        "key": "nvidia.com/gpu",
        "value": "v100"
      }
    ]
  }
}
```

#### Example 1

To create an instance type in this spec:

* Maximum 4 vCPU and at least 1 vCPU
* Maximum 16 GB Memory
* visible for all groups

```
primehub admin instancetypes create <<EOF
{
  "name": "cpu-medium",
  "displayName": "CPU Medium",
  "description": "4(1) vCPU / 16G Memory",
  "cpuLimit": 4,
  "cpuRequest": 1,
  "memoryLimit": 16,
  "global": true
}
EOF
```

#### Example 2

To create two instance types for 2 kinds of GPU workloads to a group (id: `c8cfc349-4f1b-4e36-a2b7-3ff9d4eca67a`):

* v100
* p100

Assume workloads have taints like:

* `nvidia.com/gpu=v100:NoSchedule`
* `nvidia.com/gpu=p100:NoSchedule`

It is easy to accomplish by `tolerations`

**v100**

```
primehub admin instancetypes create <<EOF
{
  "name": "gpu-v100",
  "displayName": "GPU v100",
  "description": "4 GPU v100 / 4 vCPU / 16 GB Memory",
  "gpuLimit": 4,
  "cpuLimit": 4,
  "memoryLimit": 16,
  "groups": {
    "connect": [{"id": "c8cfc349-4f1b-4e36-a2b7-3ff9d4eca67a"}]
  },
  "tolerations": {
    "set": [
      {
        "operator": "Equal",
        "effect": "NoSchedule",
        "key": "nvidia.com/gpu",
        "value": "v100"
      }
    ]
  }
}
EOF
```

**p100**

```
primehub admin instancetypes create <<EOF
{
  "name": "gpu-p100",
  "displayName": "GPU p100",
  "description": "1 GPU p100 / 4 vCPU / 16 GB Memory",
  "gpuLimit": 1,
  "cpuLimit": 4,
  "memoryLimit": 16,
  "groups": {
    "connect": [{"id": "c8cfc349-4f1b-4e36-a2b7-3ff9d4eca67a"}]
  },
  "tolerations": {
    "set": [
      {
        "operator": "Equal",
        "effect": "NoSchedule",
        "key": "nvidia.com/gpu",
        "value": "p100"
      }
    ]
  }
}
EOF
```

#### Example 3

Schedule instances to specific workloads by nodeSelector. Assume that `zone=staging` label has added to some workloads.

```
primehub admin instancetypes create <<EOF
{
  "name": "work-in-staging",
  "displayName": "cpu-staging",
  "description": "playground for staging",
  "cpuLimit": 0.5,
  "memoryLimit": 2,
  "global": true,
  "nodeSelector": {"zone": "staging"}
}
EOF
```

### Update an instance type

The input of the update command is same structure with the `create` command, but it only requires change fields.

We might change the `work-in-staging` instance type:

* increase cpuLimit to 1
* update label to `zone=staging-cpu-1`

```
primehub admin instancetypes update work-in-staging <<EOF
{
  "cpuLimit": 1,
  "nodeSelector": {"zone": "staging-cpu-1"}
}
EOF
```
