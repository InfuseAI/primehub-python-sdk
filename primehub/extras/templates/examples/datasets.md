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