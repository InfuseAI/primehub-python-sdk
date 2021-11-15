The `datasets` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all datasets in your group:

```
$ primehub datasets list
```

```
id      name    displayName    description    type
------  ------  -------------  -------------  ------
kaggle  kaggle  kaggle                        pv
```

If you already know the name of a dataset, use the `get` to get a single entry:

```
$ primehub datasets get kaggle
```

```
primehub datasets get kaggle
id:             kaggle
name:           kaggle
displayName:    kaggle
description:
type:           pv
```