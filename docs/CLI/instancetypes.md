
# Primehub Instancetypes

```
Usage: 
  primehub instancetypes <command>

Get an instance types of list instance types

Available Commands:
  get                  Get an instance type by name
  list                 List instance types

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

Get an instance type by name


```
primehub instancetypes get <name>
```

* name: the name of an instance type
 




### list

List instance types


```
primehub instancetypes list
```
 



 

## Examples

The `instancetypes` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all instance types in your group:

```
primehub instancetypes list
```

```
name                              displayName                                    description                       cpuRequest    cpuLimit    memoryRequest    memoryLimit    gpuLimit  global
--------------------------------  ---------------------------------------------  ------------------------------  ------------  ----------  ---------------  -------------  ----------  --------
cpu-2                             CPU 2                                          2 CPU / 10G                                            2                              10           0  True
gpu-1                             GPU 1                                          2 CPU / 7G / 1 GPU                       1.5           2                5              7           1  True
gpu-2                             GPU 2                                          4 CPU / 14G / 2 GPU                      4             4               14             14           2  True
cpu-1                             CPU 1                                          1 CPU / 2G                               1             1                2              2           0  True
```

If you already know the name of an instance type, use the `get` to get a single entry:

```
primehub instancetypes get cpu-1
```

```
name:           cpu-1
displayName:    CPU 1
description:    1 CPU / 2G
cpuRequest:     1
cpuLimit:       1
memoryRequest:  2
memoryLimit:    2
gpuLimit:       0
global:         True
tolerations:    [{'operator': 'Equal', 'key': 'hub.jupyter.org/dedicated', 'value': 'user', 'effect': 'NoSchedule'}]
nodeSelector:   None
```