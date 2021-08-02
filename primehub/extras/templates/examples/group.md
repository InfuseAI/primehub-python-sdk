`group` command can show the available groups for your account.

If you have the name of a group, `get` will be useful:

```
primehub group get phusers
```

The `list` command will show any groups your account belongs to:

```
primehub group list
```

```json
[
  {
    "id": "2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376",
    "name": "phusers",
    "displayName": "primehub users",
    "quotaCpu": null,
    "quotaGpu": 0,
    "quotaMemory": null,
    "projectQuotaCpu": null,
    "projectQuotaGpu": 0,
    "projectQuotaMemory": null,
    "images": [
      {
        "id": "pytorch-1",
        "name": "pytorch-1",
        "displayName": "PyTorch 1.8.0 (Python 3.7)",
        "description": "PyTorch 1.8.0 (Python 3.7)",
        "type": "both",
        "url": "infuseai/docker-stacks:pytorch-notebook-v1-8-0-63fdf50a",
        "urlForGpu": "infuseai/docker-stacks:pytorch-notebook-v1-8-0-63fdf50a-gpu-cuda-11",
        "groupName": null
      },
      {
        "id": "tf-2",
        "name": "tf-2",
        "displayName": "TensorFlow 2.5.0 (Python 3.7)",
        "description": "TensorFlow 2.5.0 (Python 3.7)",
        "type": "both",
        "url": "infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a",
        "urlForGpu": "infuseai/docker-stacks:tensorflow-notebook-v2-5-0-63fdf50a-gpu-cuda-11",
        "groupName": null
      },
      {
        "id": "base-notebook",
        "name": "base-notebook",
        "displayName": "base-notebook",
        "description": "base notebook",
        "type": "both",
        "url": "infuseai/docker-stacks:base-notebook-63fdf50a",
        "urlForGpu": "infuseai/docker-stacks:base-notebook-63fdf50a-gpu",
        "groupName": null
      },
      {
        "id": "tf-1",
        "name": "tf-1",
        "displayName": "TensorFlow 1.15.4 (Python 3.7)",
        "description": "TensorFlow 1.15.4 (Python 3.7)",
        "type": "both",
        "url": "infuseai/docker-stacks:tensorflow-notebook-v1-15-4-63fdf50a",
        "urlForGpu": "infuseai/docker-stacks:tensorflow-notebook-v1-15-4-63fdf50a-gpu",
        "groupName": null
      }
    ],
    "instanceTypes": [
      {
        "id": "cpu-1",
        "name": "cpu-1",
        "displayName": "CPU 1",
        "description": "1 CPU / 2G"
      },
      {
        "id": "gpu-2",
        "name": "gpu-2",
        "displayName": "GPU 2",
        "description": "4 CPU / 14G / 2 GPU"
      },
      {
        "id": "cpu-2",
        "name": "cpu-2",
        "displayName": "CPU 2",
        "description": "2 CPU / 10G"
      },
      {
        "id": "gpu-1",
        "name": "gpu-1",
        "displayName": "GPU 1",
        "description": "2 CPU / 7G / 1 GPU"
      }
    ],
    "datasets": []
  }
]
```

