
# Primehub Volumes

```
Usage: 
  primehub volumes <command>

Get a volume or list volumes

Available Commands:
  get                  Get a volume by name
  list                 List volumes

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

Get a volume by name


```
primehub volumes get <name>
```

* name: the name of a volume
 




### list

List volumes


```
primehub volumes list
```
 



 

## Examples

The `volumes` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all volumes in your group:

```
$ primehub volumes list
```

```
id      name    displayName    description    type
------  ------  -------------  -------------  ------
kaggle  kaggle  kaggle                        pv
```

If you already know the name of a volume, use the `get` to get a single entry:

```
$ primehub volumes get kaggle
```

```
primehub volumes get kaggle
id:             kaggle
name:           kaggle
displayName:    kaggle
description:
type:           pv
```