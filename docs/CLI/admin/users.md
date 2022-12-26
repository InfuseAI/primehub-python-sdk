
# <ADMIN> Primehub Users

```
Usage: 
  primehub admin users <command>

Manage users

Available Commands:
  add-group            Add group connection to a user by id
  create               Create a user
  delete               Delete an user by id
  get                  Get an user by id
  list                 List users
  list-groups          List groups of a user by id
  remove-group         Remove group connection from a user by id
  reset-password       Reset password by id
  update               Update the user

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### add-group

Add group connection to a user by id


```
primehub admin users add-group <id> <group_id>
```

* id: the id of a user
* group_id: group id
 




### create

Create a user


```
primehub admin users create
```
 

* *(optional)* file: The file path of the configurations




### delete

Delete an user by id


```
primehub admin users delete <id>
```

* id: the id of the user
 




### get

Get an user by id


```
primehub admin users get <id>
```

* id: the id of an user
 




### list

List users


```
primehub admin users list
```
 

* *(optional)* page: the page of all data




### list-groups

List groups of a user by id


```
primehub admin users list-groups <id>
```

* id: the id of a user
 




### remove-group

Remove group connection from a user by id


```
primehub admin users remove-group <id> <group_id>
```

* id: the id of a user
* group_id: group id
 




### reset-password

Reset password by id


```
primehub admin users reset-password <id> <password>
```

* id: password
* password
 

* *(optional)* temporary: make the password temporary




### update

Update the user


```
primehub admin users update <id>
```

* id: the id of the user
 

* *(optional)* file



 

## Examples

### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| username | required | string | lower case alphanumeric characters, '-', '.', and underscores ("_") are allowed, and must start with a letter or numeric.` |
| email | optional | string | a valid email |
| firstName | optional | string | |
| lastName | optional | string | |
| isAdmin | optional | boolean | grant the administrator role to the user |
| volumeCapacity | optional | int | customize the size of the user volume. unit: `GB`|
| groups | optional | assign the user to groups | please see the `connect` examples |

These fields are only used with email activation (only for `create`):

| field | required | type | description |
| --- | --- | --- | --- |
| sendEmail | optional | boolean | send an activation email to the user. (it worked if the smtp was set)|
| resetActions.set | optional | string[] | ask for actions, valid actions: `['VERIFY_EMAIL', 'UPDATE_PASSWORD']` |
| expiresIn | optional | int | expired duration for the activation email |

### Create users

We could create an `user1` user and assign it to a group by `groups.connect`:

```
primehub admin users create <<EOF
{
  "username": "user1",
  "groups": {
    "connect": [
      {
        "id": "fc620866-91e6-4a7e-a576-7cdfbb5e2ea7"
      }
    ]
  }
}
EOF
```

Using sendEmail and resetActions:

```
primehub admin users create <<EOF
{
  "username": "user2",
  "groups": {
    "connect": [
      {
        "id": "fc620866-91e6-4a7e-a576-7cdfbb5e2ea7"
      }
    ]
  },
  "sendEmail": true,
  "resetActions": {
    "set": [
      "VERIFY_EMAIL",
      "UPDATE_PASSWORD"
    ]
  }
}
EOF
```

After created, you could find them in the list

```
id                                    username    email                firstName    lastName    enabled    totp    isAdmin
------------------------------------  ----------  -------------------  -----------  ----------  ---------  ------  ---------
aa094096-cd5f-4941-a060-db701aa20183  phadmin     phadmin@example.com                           True       False   True
4741702f-8b8c-4011-a243-aecd16f6e007  user1                                                     True       False   False
0295ddba-f9ce-481d-be06-76ae46f7309b  user2                                                     True       False   False
```

### Reset the user's password

Reset user1's password

```
primehub admin users reset-password 4741702f-8b8c-4011-a243-aecd16f6e007 my-new-password 
```

Reset user2's password and ask for updating when the first login (by `--temporary`):

```
primehub admin users reset-password 0295ddba-f9ce-481d-be06-76ae46f7309b my-new-password --temporary
```

### Update users

You could update a user with fields you want to change:

```
primehub admin users update 4741702f-8b8c-4011-a243-aecd16f6e007 <<EOF
{"isAdmin":true}
EOF
```

### Connect and disconnect groups

List groups of a user by id

```
$ primehub admin users list-groups 4ca09a19-ef14-4800-861f-aec74149a6f4

id                                    name           displayName
------------------------------------  -------------  ---------------------------
0449b887-5c40-44ba-a945-41bc21c8d15a  InfuseAI       InfuseAI
d75ffe02-765b-4963-8ca7-7e2194d21dc7  phusers        auto generated by bootstrap
50f94220-b188-47a9-ac64-3de83438a42a  vip            VIP
```

Add a group connection to a user by id

```
$ primehub admin users add-group 4ca09a19-ef14-4800-861f-aec74149a6f4 dc6a0f50-2679-4d6b-b819-8da1b2e1b0f9
```

Remove a group connection from a user by id

```
$ primehub admin users remove-group 4ca09a19-ef14-4800-861f-aec74149a6f4 dc6a0f50-2679-4d6b-b819-8da1b2e1b0f9
```