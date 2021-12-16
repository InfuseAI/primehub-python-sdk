
# Primehub Secrets

```
Usage: 
  primehub secrets <command>

Get a secret or list secrets

Available Commands:
  get                  Get a secret by id
  list                 List secrets

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

Get a secret by id


```
primehub secrets get <id>
```

* id: the id of a secret
 




### list

List secrets


```
primehub secrets list
```
 



 

## Examples

### Query secrets

`secrets` command is used for querying secrets. You will use `id` with features that support **image pull secret**, such as the `Deployments`. 

Find all secrets with `list` command:

```
$ primehub secrets list

id              name      type
--------------  --------  ----------
image-example1  example1  kubernetes
```

Get a secret with `get` command:

```
$ primehub secrets get image-example1

id:             image-example1
name:           example1
type:           kubernetes
```