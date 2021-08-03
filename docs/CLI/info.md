
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
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group

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
Datasets:
```