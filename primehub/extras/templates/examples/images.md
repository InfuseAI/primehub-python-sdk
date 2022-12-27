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

Create a group image:

```
$ primehub images create <<EOF
{
  "name": "base-notebook-for-group-1",
  "displayName": "Base notebook for group 1",
  "description": "Base notebook for group 1",
  "type": "both",
  "url": "infuseai/base-notebook-group-1:v1",
  "urlForGpu": "infuseai/base-notebook-group-1:v1"
}
EOF
```

Or you can create a group image from json file:

```
$ primehub images create --file /tmp/base-notebook-group-1.json
```

Delete a group image:

```
$ primehub images delete base-notebook-for-group-1
```
