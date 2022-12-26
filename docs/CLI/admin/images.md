
# <ADMIN> Primehub Images

```
Usage: 
  primehub admin images <command>

Manage images

Available Commands:
  add-group            Add group connection to an image by id
  create               Create an image
  delete               Delete an image by id
  get                  Get an image by id
  list                 List images
  list-groups          List groups of an image by id
  remove-group         Remove group connection from an image by id
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


### add-group

Add group connection to an image by id


```
primehub admin images add-group <id> <group_id>
```

* id: the id of an image
* group_id: group id
 




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




### list-groups

List groups of an image by id


```
primehub admin images list-groups <id>
```

* id: the id of an image
 




### remove-group

Remove group connection from an image by id


```
primehub admin images remove-group <id> <group_id>
```

* id: the id of an image
* group_id: group id
 




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
| type | optional | string | one of ['cpu', 'gpu', 'both'], default value: 'both' |
| global | optional | boolean |  |
| groups | optional | object | |
| url | optional | string | container image url |
| urlForGpu | optional | string | container image url for GPU optimized |
| imageSpec | optional | object | the specification for customization |
| useImagePullSecret | optional | string | the id of a secret |

*Note: imageSpec cannot use with url and urlForGpu*

#### useImagePullSecret

The secret can be found with `primehub admin secrets list`

```
$ primehub admin secrets list

id                             name               displayName        type        registryHost         username
-----------------------------  -----------------  -----------------  ----------  -------------------  ----------
image-my-image-registry        my-image-registry  my-image-registry  kubernetes  registry.gitlab.com  nobody
gitsync-secret-dataset-secret  dataset-secret     dataset-secret     opaque
```

Please pick up a secret with `kubernetes` type. For example, `image-my-image-registry` can be used for useImagePullSecret.


#### imageSpec Example

> YOU MUST ENABLE AND CONFIGURE [CUSTOM IMAGE BUILD](https://docs.primehub.io/docs/getting_started/configure-image-builder)

To use the imageSpec, you need an object like this structure:

```json
{
  "baseImage": "jupyter/base-notebook",
  "packages": {
    "pip": [
      "pytest"
    ]
  }
}
```

* baseImage: a container url for the customization
* packages: configure package managers and installation list
    * pip
    * apt
    * conda

`packages` is a dictionary and its keys should be one of `['apt', 'conda', 'pip']` and value should be a list for
packages you want to install

### Manage images by SDK

First, you can find the example by `create` action:

```
$ primehub admin images create

The configuration is required.

Example:
{
  "name": "base",
  "displayName": "Base image",
  "description": "base-notebook with python 3.7",
  "type": "both",
  "url": "infuseai/docker-stacks:base-notebook-63fdf50a",
  "urlForGpu": "infuseai/docker-stacks:base-notebook-63fdf50a-gpu",
  "global": true
}
```

Let's use it to create a new image:

```
$ primehub admin images create <<EOF
{
  "name": "my-first-image",
  "displayName": "Learning how to create an image from SDK",
  "description": "base-notebook with python 3.7",
  "type": "both",
  "url": "infuseai/docker-stacks:base-notebook-63fdf50a",
  "urlForGpu": "infuseai/docker-stacks:base-notebook-63fdf50a-gpu",
  "global": true
}
EOF
```

And check the result by `list` action

```
$ primehub admin images list

id              name            displayName                               description                     type    isReady
--------------  --------------  ----------------------------------------  ------------------------------  ------  ---------
base-notebook   base-notebook   base-notebook                             base notebook                   both    True
pytorch-1       pytorch-1       PyTorch 1.8.0 (Python 3.7)                PyTorch 1.8.0 (Python 3.7)      both    True
tf-1            tf-1            TensorFlow 1.15.4 (Python 3.7)            TensorFlow 1.15.4 (Python 3.7)  both    True
tf-2            tf-2            TensorFlow 2.5.0 (Python 3.7)             TensorFlow 2.5.0 (Python 3.7)   both    True
my-first-image  my-first-image  Learning how to create an image from SDK  base-notebook with python 3.7   both    True
```

### Build a custom build

```
$ primehub admin images create <<EOF
{
  "name": "my-custom-image",
  "type": "both",
  "global": true,
  "imageSpec": {
    "baseImage": "jupyter/base-notebook",
    "packages": {
      "pip": [
        "pytest"
      ]
    }
  }
}
EOF
```