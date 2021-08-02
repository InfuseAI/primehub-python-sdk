The `images` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all images in your group:

```
primehub images list
```

```json
[
  {
    "id": "pytorch-1",
    "name": "pytorch-1",
    "displayName": "PyTorch 1.8.0 (Python 3.7)",
    "description": "PyTorch 1.8.0 (Python 3.7)",
    "useImagePullSecret": null,
    "spec": {
      "description": "PyTorch 1.8.0 (Python 3.7)",
      "displayName": "PyTorch 1.8.0 (Python 3.7)",
      "type": "both",
      "url": "infuseai/docker-stacks:pytorch-notebook-v1-8-0-63fdf50a",
      "urlForGpu": "infuseai/docker-stacks:pytorch-notebook-v1-8-0-63fdf50a-gpu-cuda-11"
    }
  },
  {
    "id": "tf-2",
    "name": "tf-2",
    "displayName": "TensorFlow 2.5.0 (Python 3.7)",
    "description": "TensorFlow 2.5.0 (Python 3.7)",
    "useImagePullSecret": null,
    "spec": {
      "description": "TensorFlow 2.5.0 (Python 3.7)",
      "displayName": "TensorFlow 2.5.0 (Python 3.7)",
      "type": "both",
      "url": "infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a",
      "urlForGpu": "infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a-gpu-cuda-11"
    }
  },
  {
    "id": "base-notebook",
    "name": "base-notebook",
    "displayName": "base-notebook",
    "description": "base notebook",
    "useImagePullSecret": null,
    "spec": {
      "description": "base notebook",
      "displayName": "base-notebook",
      "type": "both",
      "url": "infuseai/docker-stacks:base-notebook-63fdf50a",
      "urlForGpu": "infuseai/docker-stacks:base-notebook-63fdf50a-gpu"
    }
  },
  {
    "id": "tf-1",
    "name": "tf-1",
    "displayName": "TensorFlow 1.15.4 (Python 3.7)",
    "description": "TensorFlow 1.15.4 (Python 3.7)",
    "useImagePullSecret": null,
    "spec": {
      "description": "TensorFlow 1.15.4 (Python 3.7)",
      "displayName": "TensorFlow 1.15.4 (Python 3.7)",
      "type": "both",
      "url": "infuseai/docker-stacks:tensorflow-notebook-v1-15-4-63fdf50a",
      "urlForGpu": "infuseai/docker-stacks:tensorflow-notebook-v1-15-4-63fdf50a-gpu"
    }
  }
]
```

If you already know the name of a images, use the `get` to get a single entry:

```
primehub images get tf-2
```

```json
{
  "id": "tf-2",
  "name": "tf-2",
  "displayName": "TensorFlow 2.5.0 (Python 3.7)",
  "description": "TensorFlow 2.5.0 (Python 3.7)",
  "useImagePullSecret": null,
  "spec": {
    "description": "TensorFlow 2.5.0 (Python 3.7)",
    "displayName": "TensorFlow 2.5.0 (Python 3.7)",
    "type": "both",
    "url": "infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a",
    "urlForGpu": "infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a-gpu-cuda-11"
  }
}
```