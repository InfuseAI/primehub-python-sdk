
# Primehub Images

```
Usage: 
  primehub images <command>

Get a image or list images

Available Commands:
  get                  Get a image by name
  list                 List images

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

Get a image by name


```
primehub images get <name>
```

* name: the name of an image
 




### list

List images


```
primehub images list
```
 



 

## Examples

The `images` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all images in your group:

```
primehub images list
```

```name           displayName                     description
-------------  ------------------------------  ------------------------------
pytorch-1      PyTorch 1.8.0 (Python 3.7)      PyTorch 1.8.0 (Python 3.7)
tf-2           TensorFlow 2.5.0 (Python 3.7)   TensorFlow 2.5.0 (Python 3.7)
base-notebook  base-notebook                   base notebook
tf-1           TensorFlow 1.15.4 (Python 3.7)  TensorFlow 1.15.4 (Python 3.7
```

If you already know the name of a images, use the `get` to get a single entry:

```
primehub images get tf-2
```

```
id:                  tf-2
name:                tf-2
displayName:         TensorFlow 2.5.0 (Python 3.7)
description:         TensorFlow 2.5.0 (Python 3.7)
useImagePullSecret:  None
spec:
  description:       TensorFlow 2.5.0 (Python 3.7)
  displayName:       TensorFlow 2.5.0 (Python 3.7)
  type:              both
  url:               infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a
  urlForGpu:         infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a-gpu-cuda-11
```