The `instancetypes` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all instance types in your group:

```
primehub instancetypes list
```

```
id     name    displayName    description
-----  ------  -------------  -------------------
cpu-1  cpu-1   CPU 1          1 CPU / 2G
gpu-2  gpu-2   GPU 2          4 CPU / 14G / 2 GPU
cpu-2  cpu-2   CPU 2          2 CPU / 10G
gpu-1  gpu-1   GPU 1          2 CPU / 7G / 1 GPU
```

If you already know the name of an instance type, use the `get` to get a single entry:

```
primehub instancetypes get cpu-1
```

```
id:             cpu-1
name:           cpu-1
displayName:    CPU 1
description:    1 CPU / 2G
```