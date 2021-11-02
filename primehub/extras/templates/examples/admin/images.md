### Fields for creating or updating

TODO: update this

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

