### Query secrets

`secrets` command is used for querying secrets. You will use `id` with features that support **image pull secret**, such as the `Deployments`. 

Find all secrets with `list` command:

```
$ primehub secrets list

id              name      type
--------------  --------  ----------
image-example1  example1  kubernetes
```

Get a secret with `get` command:

```
$ primehub secrets get image-example1

id:             image-example1
name:           example1
type:           kubernetes
```
