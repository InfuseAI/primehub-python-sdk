
# Primehub Config

```
Usage: 
  primehub config <command>

Update the settings of PrimeHub SDK

Available Commands:
  generate-token       Generate Token Flow
  set-endpoint         Set endpoint and save to the config file
  set-group            Set group and save to the config file
  set-token            Set token and save to the config file

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### generate-token

Generate Token Flow


```
primehub config generate-token <server_url>
```

* server_url: PrimeHub's URL
 




### set-endpoint

Set endpoint and save to the config file


```
primehub config set-endpoint <endpoint>
```

* endpoint: an URL to GraphQL API endpoint
 




### set-group

Set group and save to the config file


```
primehub config set-group <group>
```

* group: group name
 




### set-token

Set token and save to the config file


```
primehub config set-token <token>
```

* token: a token used by GraphQL request
 



 

## Examples

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

### Example: generate API Token with OAuth login

```
primehub config generate-token http://primehub-python-sdk.primehub.io
```

The commands will guide you how to get an API token, it will show 2 required actions:
* visit the URL and login with your account and copy the authorization code from the web page
* paste the authorization code back to the terminal


```
Go to this URL in the browser http://primehub-python-sdk.primehub.io/console/oidc/auth-flow/request
Enter your authorization code:
```

When all actions have done, the configuration got updated:

```
Found old configuration, backup it to /home/phadmin/.primehub/config-20211001161504.json
PrimeHub SDK Config has been updated: /home/phadmin/.primehub/config.json
```