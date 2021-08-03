The `config` command provides the ability to update the PrimeHub SDK configuration file. The file locates
at `~/.primehub/config.json` by default.

> Be careful with the config command, it will `MODIFY` the configuration file directly

### Example: create a config file

We could use the `config` command with the `--config` flag to make a new config to the `my.config` path.

```
primehub config set-endpoint http://primehub-python-sdk.primehub.io --config my-config.json
primehub config set-token my-token --config my-config.json
primehub config set-group no-such-group --config my-config.json
```

You might see the warning, because of the fake endpoint:

```
2021-08-03 11:05:17,209 - cmd-config - WARNING - Got request problem with http://primehub-python-sdk.primehub.io: HTTPConnectionPool(host='primehub-python-sdk.primehub.io', port=80): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a170cd0>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))
No group information for [no-such-group], please set the right group
```

However, `config` still create the file for you:

```json
{
  "endpoint": "http://primehub-python-sdk.primehub.io",
  "api-token": "my-token",
  "group": {
    "name": null
  }
}
```

The SDK can not fetch the group information from the server, finally you got a group with null name. If you did
configure with a real api server, the group information would be available:

```json
{
  "endpoint": "http://primehub-python-sdk.primehub.io",
  "api-token": "my-token",
  "group": {
    "id": "927406f6-88b0-490e-8e36-7835224fdf13",
    "name": "sdk",
    "displayName": "PrimeHub Python SDK Team"
  }
}
```

