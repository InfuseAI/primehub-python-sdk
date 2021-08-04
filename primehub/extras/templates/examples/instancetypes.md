The `instancetypes` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all instance types in your group:

```
primehub instancetypes list
```

```json
[
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
]
```

If you already know the name of an instance type, use the `get` to get a single entry:

```
primehub instancetypes get cpu-1
```

```json
{
  "id": "cpu-1",
  "name": "cpu-1",
  "displayName": "CPU 1",
  "description": "1 CPU / 2G"
}
```