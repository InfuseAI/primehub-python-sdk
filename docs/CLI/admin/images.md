
# <ADMIN> Primehub Images

```
Usage: 
  primehub admin images <command>

Manage images

Available Commands:
  create               Create an image
  delete               Delete an image by id
  get                  Get an image by id
  list                 List images
  update               Update the image

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

Create an image


```
primehub admin images create
```
 

* *(optional)* file: The file path of the configurations




### delete

Delete an image by id


```
primehub admin images delete <id>
```

* id: the id of an image
 




### get

Get an image by id


```
primehub admin images get <id>
```

* id: the id of an image
 




### list

List images


```
primehub admin images list
```
 

* *(optional)* page: the page of all data




### update

Update the image


```
primehub admin images update <id>
```

* id: the id of the image
 

* *(optional)* file



 

## Examples

### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| name | required | string | it should be a valid resource name for kubernetes. `name` will be ignored when updating |
| displayName | optional | string | |
| description | optional | string | |
| type | required | string | onf of ['cpu', 'gpu', 'both'] |
| global | optional | boolean |  |
| groups | optional | object | |
| url | optional | string | container image url |
| urlForGpu | optional | string | container image url for GPU optimized |
| imageSpec | optional | object | |

