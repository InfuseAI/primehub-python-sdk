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