`me` command shows the account information. It is useful when you have no idea with your api-token belongs to which
user.

```
primehub me
```

```json
{
  "id": "a7db12dc-04fa-419c-9cd7-af768575a871",
  "username": "phadmin",
  "firstName": null,
  "lastName": null,
  "email": "dev+phadmin@infuseai.io",
  "isAdmin": true
}
```

### Notes

The two commands are the same, because the `me` command group only has one command `me`, it could use shortcut form:

```
# shortcut form
primehub me
```

```
#        <command-group> <command>
primehub me              me
```

