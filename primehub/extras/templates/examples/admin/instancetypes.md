### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| name | required | string | it should be a valid resource name for kubernetes. `name` will be ignored when updating |
| displayName | optional | string | display name for the instance type |
| description | optional | string | |
| global | optional | boolean | when an instance type is global, it could be seen for each group |
| groups | optional | list of connected groups (dict) | please see the `connect` examples. default value: false |
| cpuLimit | required* | float | the maximum vCPU quantity. For example: `1` or `1.0` means 1 vCPU and `0.5` means half of vCPU |
| cpuRequest | optional | float | the initial vCPU quantity for CPU resource. cpuRequest can not be greater than cpuLimit |
| memoryLimit | required* | float | the maximum Memory size. For example: `1.5` means `1.5 GB` memory |
| memoryRequest | optional | float | the initial Memory size. memoryRequest can not be greater than memoryLimit |
| gpuLimit | optional | int | the count of GPU when an instance allocated |
| tolerations | optional | dict | kubernetes pod toleration in an instance (Pod) |
| nodeSelector | optional | dict | kubernetes pod nodeSelector in an instance (Pod) |

#### Auto-filling Fields
Auto-filling will happen when the configuration omitted fields

| field	| value	| description |
| --- | --- | --- |
| cpuLimit	| 1	| 1 vCPU |
| memoryLimit	| 1	| 1 GB memory |

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

### Connect and disconnect groups

List groups of an instance type by id:

```
$ primehub admin instancetypes list-groups gpu-2

id                                    name                     displayName
------------------------------------  -----------------------  ---------------------------
71ac1e32-65fa-4e8e-a735-ba282e3149b1  example-group-1          Example Group 1
0fdaea59-705a-4546-8d13-2d52511342b0  example-group-2          Example Group 2
```
* Please note it will return empty list if the instance type is at global scope

Add a group connection to an instance type by id

```
$ primehub admin instancetypes add-group gpu-2 dc6a0f50-2679-4d6b-b819-8da1b2e1b0f9
```

Remove a group connection from an instance type by id

```
$ primehub admin instancetypes remove-group gpu-2 71ac1e32-65fa-4e8e-a735-ba282e3149b1
```
