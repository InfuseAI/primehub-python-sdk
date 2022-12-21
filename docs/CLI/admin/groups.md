
# <ADMIN> Primehub Groups

```
Usage: 
  primehub admin groups <command>

Manage groups

Available Commands:
  add-user             Add the user to the group
  connect-image        Make the image join the group
  create               Create a group
  create-image         Add the image to the group
  delete               Delete the group by id
  disconnect-image     Make the image leave the group
  get                  Get the group info by id
  list                 List groups
  list-images          List images in the group
  list-users           List users in the group
  remove-user          Remove the user from the group
  update               Update the group

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### add-user

Add the user to the group


```
primehub admin groups add-user <group_id> <user_id>
```

* group_id: the group id
* user_id: the user id
 

* *(optional)* enable_group_admin




### connect-image

Make the image join the group


```
primehub admin groups connect-image <group_id> <image_id>
```

* group_id: The group id
* image_id: The image id
 




### create

Create a group


```
primehub admin groups create
```
 

* *(optional)* file: the file path of the configurations




### create-image

Add the image to the group


```
primehub admin groups create-image <group_id>
```

* group_id: The group id
 

* *(optional)* file: The file path of the configurations




### delete

Delete the group by id


```
primehub admin groups delete <id>
```

* id: the group id
 




### disconnect-image

Make the image leave the group


```
primehub admin groups disconnect-image <group_id> <image_id>
```

* group_id: The group id
* image_id: The image id
 




### get

Get the group info by id


```
primehub admin groups get <id>
```

* id: the group id
 




### list

List groups


```
primehub admin groups list
```
 

* *(optional)* page: the page of all data




### list-images

List images in the group


```
primehub admin groups list-images <group_id>
```

* group_id: The group id
 




### list-users

List users in the group


```
primehub admin groups list-users <group_id>
```

* group_id: the group id
 




### remove-user

Remove the user from the group


```
primehub admin groups remove-user <group_id> <user_id>
```

* group_id: the group id
* user_id: the user id
 

* *(optional)* disable_group_admin




### update

Update the group


```
primehub admin groups update <id>
```

* id: the group id
 

* *(optional)* file: the file path of the configurations



 

## Examples

### Fields for creating or updating

| field              | required | type                                   | description                                                                                                                                             |
|--------------------|----------|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| name               | required | string                                 | must start with a letter or numeric, '-' and '_' are allowed, and the length should be more than 2.                                                     |
| displayName        | optional | string                                 | display name                                                                                                                                            |
| quotaCpu           | optional | float                                  | how many CPU can be used by the user within this group, default: 0.5                                                                                    |
| quotaGpu           | optional | int                                    | how many GPU can be used by the user within this group, default: 0                                                                                      |
| quotaMemory        | optional | float                                  | how many memory can be used by the user within this group, default: unlimited GB                                                                        | 
| projectQuotaCpu    | optional | float                                  | how many CPU can be shared by all users in the group, default: unlimited                                                                                |
| projectQuotaGpu    | optional | int                                    | how many GPU can be shared by all users in the group, default: unlimited                                                                                |
| projectQuotaMemory | optional | float                                  | how many memory can be shared by all users in the group, default: unlimited GB                                                                          |
| admins             | optional | string                                 | assign admin user of the group, multiple users are able to be assigned (see [also](https://docs.primehub.io/docs/guide_manual/admin-group#group-admin)) |
| users              | optional | assign / dissociate users to the group | please see the connect / disconnect examples                                                                                                            |

*Note: user resource quota should not greater than project resource quota. e.g., `quotaCpu <= projectQuotaCpu`*

#### Model Deployment

Groups with enabled model deployment are able to deploy/serve models. (
see [also](https://docs.primehub.io/docs/guide_manual/admin-group#model-deployment))

`maxDeploy` is used when `enabledDeployment` is enable:

| field             | required | type    | description                                       |
|-------------------|----------|---------|---------------------------------------------------|
| enabledDeployment | optional | boolean | enable model deployment                           |
| maxDeploy         | optional | int     | limit on the amount of deployments for this group |

#### Shared Volume

The created shared volume is shared among members in the group. (
see [also](https://docs.primehub.io/docs/guide_manual/admin-group#shared-volume))

`sharedVolumeCapacity` is used when `enabledSharedVolume` is enable:

| field                | required | type    | description                             |
|----------------------|----------|---------|-----------------------------------------|
| enabledSharedVolume  | optional | boolean | enable share volume                     |
| sharedVolumeCapacity | optional | int     | the capacity of the shared volume in GB |

### Create a group

We could create a `test_group_1` group and assign admin users and multiple users `users.connect`:

```
primehub admin groups create <<EOF
{
  "name": "test_group_1",
  "displayName": "test group",
  "enabledDeployment": true,
  "enabledSharedVolume": true,
  "quotaCpu": 0.5,
  "quotaGpu": 1,
  "quotaMemory": 2,
  "maxDeploy": 3,
  "sharedVolumeCapacity": 1,
  "admins": "test_user_1,test_user_2",
  "users": {
    "connect": [
      {
        "id": "451e78f0-9877-4679-8501-3b626d41688c"
      },
      {
        "id": "57145a52-e28b-4ccf-90c4-984f8afe7179"
      },
      {
        "id": "96051b60-a8f5-49b6-937f-474f2237a952"
      }
    ]
  }
}
EOF
```

After created, you could find them in the list

```
primehub admin groups list
```

```
id                                    displayName           name                          admins                     quotaCpu    quotaGpu    quotaMemory  projectQuotaCpu    projectQuotaGpu    projectQuotaMemory      sharedVolumeCapacity
------------------------------------  --------------------  ----------------------------  -----------------------  ----------  ----------  -------------  -----------------  -----------------  --------------------  ----------------------
ed8b465d-593a-482a-a9f6-b97c37e8abcb  primehub users        phusers                       phadmin
bd3d499c-0354-407d-b45a-08cf20d1a8b7  test group            test_group_1                  test_user1,test_user2           0.5           1              2                                                                                   1
```

### Update a group

You could update a group with fields you want to change:  
(e.g., update the `test_group_1` group to dissociate user `users.disconnect`)

```
primehub admin users update bd3d499c-0354-407d-b45a-08cf20d1a8b7 <<EOF
{
  "admins": "test_user_1",
  "users": {
    "disconnect": [
      {
        "id": "96051b60-a8f5-49b6-937f-474f2237a952"
      }
    ]
  }
}
EOF
```

### Manipulate users in a group

`list-users` will show users in a group with their id, username and group_admin permission:

```
$ primehub admin groups list-users 149f4cb6-e8d1-44e8-93d4-3a77f46ac682
id                                    username    group_admin
------------------------------------  ----------  -------------
698da31d-2ef8-476d-9d56-6275a949402c  foo         False
c634f8c9-d22e-4ead-bfa2-21ed018f6029  phadmin     True
```

`add-user` and `remove-user` have same arguments to add or remove a user from the group,
but they are also do the group-admin enabling and disable.

You can add an existing user with `--enable_group_admin` to added the group admin permission:

```
$ primehub admin groups add-user 149f4cb6-e8d1-44e8-93d4-3a77f46ac682 698da31d-2ef8-476d-9d56-6275a949402c --enable_group_admin
```

The permission can disable with `remove-user` and `--disable_group_admin`. When `--disable_group_admin` has set,
removal operation will only remove the permission not the user.