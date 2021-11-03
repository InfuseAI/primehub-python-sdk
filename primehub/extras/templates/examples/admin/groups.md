### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| name | required | string | must start with a letter or numeric, '-' and '_' are allowed, and the length should be more than 2. |
| displayName | optional | string | display name |
| enabledDeployment | optional | boolean | groups with enabled model deployment are able to deploy/serve models |
| enabledSharedVolume | optional | boolean | the shared volume is shared among members in the group. |
| quotaCpu | optional | float | how many CPU can be used by the user within this group, default: 0.5 |
| quotaGpu | optional | int | how many GPU can be used by the user within this group, default: 0 |
| quotaMemory | optional | float | how many memory can be used by the user within this group, default: unlimited GB | 
| projectQuotaCpu | optional | float |  how many CPU can be shared by all users in the group, default: unlimited |
| projectQuotaGpu | optional | int | how many GPU can be shared by all users in the group, default: unlimited |
| projectQuotaMemory| optional | float | how many memory can be shared by all users in the group, default: unlimited GB |
| admins | optional | string | assign admin user of the group, multiple users are able to be assigned (see [also](https://docs.primehub.io/docs/guide_manual/admin-group#group-admin)) |
| users | optional | assign / dissociate users to the group | please see the connect / disconnect examples |

`maxDeploy` is used when `enabledDeployment` is enable:

| field | required | type | description |
| --- | --- | --- | --- |
| maxDeploy | optional | int | limit on the amount of deployments for this group |

`sharedVolumeCapacity` is used when `enabledSharedVolume` is enable:

| field | required | type | description |
| --- | --- | --- | --- |
| sharedVolumeCapacity | optional | int | the capacity of the shared volume in GB |

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
  "launchGroupOnly": true,
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