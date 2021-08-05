
# Primehub Groups

```
Usage: 
  primehub groups <command>

Get a group or list groups

Available Commands:
  get                  Get group by name
  list                 List groups

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group

```


### get

Get group by name


```
primehub groups get <group_name>
```

* group_name: the name of a group
 




### list

List groups


```
primehub groups list
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

```json
[
  {
    "id": "2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376",
    "name": "phusers",
    "displayName": "primehub users",
    "quotaCpu": null,
    "quotaGpu": 0,
    "quotaMemory": null,
    "projectQuotaCpu": null,
    "projectQuotaGpu": 0,
    "projectQuotaMemory": null
  }
]
```
