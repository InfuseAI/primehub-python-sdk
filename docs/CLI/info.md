
# Primehub Info

```
Usage: 
  primehub info <command>

Display the user information and the selected group information

Available Commands:
  info                 Show PrimeHub Cli information

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### info

Show PrimeHub Cli information


```
primehub info info
```
 



 

## Examples

`info` command is only for `primehub` command line. It shows a human-readable output that gives your an outline under
the account:

```
primehub info
```

```
Endpoint: https://example.primehub.io/api/graphql
User:
  Id: a7db12dc-04fa-419c-9cd7-af768575a871
  Username: phadmin
  Email: dev+phadmin@infuseai.io
  First Name: None
  Last Name: None
  Is Admin: True
Current Group:
  Id: 2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376
  Name: phusers
  Display Name: primehub users
  Group Quota:
    CPU: None
    GPU: 0
    Memory: None
  User Quota:
    CPU: None
    GPU: 0
    Memory: None
Images:
  pytorch-1
  tf-2
  base-notebook
  tf-1
InstanceTypes:
  cpu-1
  gpu-2
  cpu-2
  gpu-1
Volumes:
```

### Notes

The two commands are the same, because the `info` command group only has one command `info`, it could use shortcut form:

```
# shortcut form
primehub info
```

```
#        <command-group> <command>
primehub info            info
```
