
# Primehub Groups

```
Usage: 
  primehub groups <command>

Get a group or list groups

Available Commands:
  add-user             Add a user to a group by id
  get                  Get group by name
  list                 List groups
  remove-user          Remove a user from a group by id

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
 




### list

List groups


```
primehub groups list
```
 




### remove-user

Remove a user from a group by id


```
primehub groups remove-user <group_id> <user_id>
```

* group_id: group id
* user_id: user id
 



 

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
