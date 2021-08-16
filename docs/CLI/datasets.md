
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

The `datasets` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all datasets in your group:

```
primehub datasets list
```

```json
[
  {
    "id": "tensorflow-dataset",
    "name": "tensorflow-dataset",
    "displayName": "tensorflow-dataset",
    "description": "",
    "type": "git"
  },
  {
    "id": "pv-dataset",
    "name": "pv-dataset",
    "displayName": "pv-dataset",
    "description": "",
    "type": "pv"
  },
  {
    "id": "primehub",
    "name": "primehub",
    "displayName": "PrimeHub Config",
    "description": "PrimeHub Config",
    "type": "env"
  }
]
```

If you already know the name of a dataset, use the `get` to get a single entry:

```
primehub datasets get primehub
```

```json
{
  "id": "primehub",
  "name": "primehub",
  "displayName": "PrimeHub Config",
  "description": "PrimeHub Config",
  "type": "env"
}
```