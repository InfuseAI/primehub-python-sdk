
# <ADMIN> Primehub Secrets

```
Usage: 
  primehub admin secrets <command>

Manage secrets

Available Commands:
  create               Create a secret
  delete               Delete a secret by id
  get                  Get an secret by id
  list                 List secrets
  update               Update the secret

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### create

Create a secret


```
primehub admin secrets create
```
 

* *(optional)* file: The file path of the configurations




### delete

Delete a secret by id


```
primehub admin secrets delete <id>
```

* id: the id of the secret
 




### get

Get an secret by id


```
primehub admin secrets get <id>
```

* id: the id of a secret
 




### list

List secrets


```
primehub admin secrets list
```
 

* *(optional)* page: the page of all data




### update

Update the secret


```
primehub admin secrets update <id>
```

* id: the id of the secret
 

* *(optional)* file



 

## Examples

### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| name | required | string | The name of secret. It is only used when creating. |
| type | required | string | one of ['opaque', 'kubernetes']. `opaque` is used for Git Sync Volume (SSH Public Key). `kubernetes` is used for Container Registry. |
| displayName | optional | string | |

* `type` can not be changed after created.

Fields for  `opaque`

| field | required | type | description |
| --- | --- | --- | --- |
| secret | conditional | string | when type is opaque, secret field become required for the SSH Public Key. |

Fields for  `kubernetes`

You should put container registry credentials to these fields:

| field | required | type | description |
| --- | --- | --- | --- |
| registryHost | conditional | string |  |
| username | conditional | string | |
| password | conditional | string | |

### Create secrets

Create a secret for a Git Sync volume

```
primehub admin secrets create <<EOF
{
    "name": "dataset-secret",
    "type": "opaque",
    "secret": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDNoaA3Eo3CjCUBVe0SbrzsfOKS3REkfTkl28/drVVW5B+NXaXH7b3p7xijL8RTFj/wXQggACY+rcNtMbYewgxpZd1OZSf52JkqPKUfPHhvl3jGgeSSSg3fn6LAbAS8Vv/ywRJVsLVsjQelM1OH3E64Mznt0qpl/gO//T2CgRNHTwBseFMOf0BNfkd+gsP046pNxwqMlLfytrt6UC4+0Rb6ZWgVfd/Ij4xzK1AB/3mJ8HEdoCRWvoI/IElTzcEvvK3Vrx1KtSugpfywTXjSAyJhRWO7RsvgLvBgkuKRWFYuGlDo/X84hSClCFagPZ7LmvxIEgGFsUn6XFgia7VAO+WD nobody@local"
}
EOF
```

Create a secret for the Image Pull Secret usage

```
primehub admin secrets create <<EOF
{
    "name": "my-image-registry",
    "type": "kubernetes",
    "registryHost": "registry.gitlab.com",
    "username": "nobody",
    "password": "password"
}
EOF
```

### Query secrets

Using `list` to find all secrets in the PrimeHub

```
$ primehub admin secrets list

id                             name               displayName        type        registryHost         username
-----------------------------  -----------------  -----------------  ----------  -------------------  ----------
image-my-image-registry        my-image-registry  my-image-registry  kubernetes  registry.gitlab.com  nobody
gitsync-secret-dataset-secret  dataset-secret     dataset-secret     opaque
```

Using `get` to get a secret

```
$ primehub admin secrets get image-my-image-registry

id:             image-my-image-registry
name:           my-image-registry
displayName:    my-image-registry
type:           kubernetes
registryHost:   registry.gitlab.com
username:       nobody
password:       ******
```

```
$ primehub admin secrets get gitsync-secret-dataset-secret

id:             gitsync-secret-dataset-secret
name:           dataset-secret
displayName:    dataset-secret
type:           opaque
```

### Update a secret

Updating is similar with creating

* update with the id of the secret
* don't put `name` in the payload
* `type` cannot not be changed

```
primehub admin secrets update image-my-image-registry <<EOF
{
    "type": "kubernetes",
    "registryHost": "registry.gitlab.com",
    "username": "somebody",
    "password": "password"
}
EOF
```

After updating, **nobody** becomes **somebody**

```
$ primehub admin secrets list

id                             name               displayName        type        registryHost         username
-----------------------------  -----------------  -----------------  ----------  -------------------  ----------
gitsync-secret-dataset-secret  dataset-secret     dataset-secret     opaque
image-my-image-registry        my-image-registry  my-image-registry  kubernetes  registry.gitlab.com  somebody
```

### Delete a secret

The deletion needs asking for the permission:

```
$ primehub admin secrets delete image-my-image-registry

User rejects action [delete], please use the flag "--yes-i-really-mean-it" to allow the action.
```

If you really want to do it, adding `--yes-i-really-mean-it`

```
$ primehub admin secrets delete image-my-image-registry --yes-i-really-mean-it

id:             image-my-image-registry
```