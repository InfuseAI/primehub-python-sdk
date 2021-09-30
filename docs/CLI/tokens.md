
# Primehub Tokens

```
Usage: 
  primehub tokens <command>

Manage the api-token

Available Commands:
  generate-token       Generate Token Flow

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
primehub tokens generate-token <api_token_endpoint>
```

* api_token_endpoint: the api-token service endpoint
 



 

## Examples

### Example: generate the api-token and update the configuration file

The API Token generator needs an api-token-service endpoint

```
http://example.primehub.io/api/api-token
```

When you run `generate-token`, it will show you a URL to visit:

* visit the URL in your browser
* please login with your PrimeHub account if it asks for login
* copy the `authorization code` and paste to the console

```
primehub tokens generate-token http://example.primehub.io/api/api-token
Go to this URL in the browser http://example.primehub.io/api/api-token/request
Enter your authorization code:
```

After finished, the configuration will be updated:

```
Found old configuration, backup it to /home/phadmin/.primehub/config-20210930165339.json
PrimeHub SDK Config has been updated: /home/phadmin/.primehub/config.json
```