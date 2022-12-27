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

### Connect and disconnect groups

List groups of an image by id

```
$ primehub admin images list-groups base-notebook

id                                    name                     displayName
------------------------------------  -----------------------  ---------------------------
71ac1e32-65fa-4e8e-a735-ba282e3149b1  example-group-1          Example Group 1
0fdaea59-705a-4546-8d13-2d52511342b0  example-group-2          Example Group 2
```
* Please note it will return empty list if the image is at global scope

Add a group connection to an image by id

```
$ primehub admin images add-group base-notebook dc6a0f50-2679-4d6b-b819-8da1b2e1b0f9
```

Remove a group connection from an image by id

```
$ primehub admin images remove-group base-notebook 71ac1e32-65fa-4e8e-a735-ba282e3149b1
```
