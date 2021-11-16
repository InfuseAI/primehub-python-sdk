The `volumes` command is a group specific resource. It only works after the `group` assigned.

Using `list` to find all volumes in your group:

```
$ primehub volumes list
```

```
id      name    displayName    description    type
------  ------  -------------  -------------  ------
kaggle  kaggle  kaggle                        pv
```

If you already know the name of a volume, use the `get` to get a single entry:

```
$ primehub volumes get kaggle
```

```
primehub volumes get kaggle
id:             kaggle
name:           kaggle
displayName:    kaggle
description:
type:           pv
```
