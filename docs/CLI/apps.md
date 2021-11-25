
# Primehub Apps

```
Usage: 
  primehub apps <command>

Manage PrimeHub Applications

Available Commands:
  create               Install an application
  delete               Stop the PrimeHub Application
  get                  Get the PrimeHub Application
  list                 List PrimeHub Applications
  logs                 Get logs of the PrimeHub Application by id
  start                Start the PrimeHub Application
  stop                 Stop the PrimeHub Application
  update               Update an application

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

Install an application


```
primehub apps create
```
 

* *(optional)* file: The file path of PrimeHub application configuration




### delete

Stop the PrimeHub Application


```
primehub apps delete <id>
```

* id
 




### get

Get the PrimeHub Application


```
primehub apps get <id>
```

* id
 




### list

List PrimeHub Applications


```
primehub apps list
```
 




### logs

Get logs of the PrimeHub Application by id


```
primehub apps logs <id>
```

* id: The job id
 

* *(optional)* follow: Wait for additional logs to be appended

* *(optional)* tail: Show last n lines




### start

Start the PrimeHub Application


```
primehub apps start <id>
```

* id
 




### stop

Stop the PrimeHub Application


```
primehub apps stop <id>
```

* id
 




### update

Update an application


```
primehub apps update <id>
```

* id: The id of PrimeHub application
 

* *(optional)* file: The file path of PrimeHub application configuration



 

## Examples

### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| templateId | required | string | The id of a PhAppTemplate *only used with creating*|
| id | required* | string | The id of a PhApp *only used with creating* |
| displayName | required | string |  |
| instanceType | required | string |  |
| scope | required | string | one of `[public, primehub, group]` |
| env | optional | EnvVar[] | a list of EnvVar |

#### EnvVar

EnvVar is a dict with `name` and `value` with string values:

```json
{
  "name": "my_var",
  "value": "1"
}
```

### Auto-filling Fields

Auto-filling will happen when the inputs omitted fields

| field | value | comment |
| --- | --- | --- |
| id | {templateId}-{random-hex} | Generate a valid PhApp id from the templateId |

### Creating

The `create` action helps you to install a new PrimeHub application. It shows an example that can be used to create
a `code-server` application:

```
$ primehub apps create
PrimeHub application configuration is required.

Example:
{
  "templateId": "code-server",
  "id": "code-server-26fcc",
  "displayName": "my-code-server-26fcc",
  "env": [
    {
      "name": "key1",
      "value": "value1"
    }
  ],
  "instanceType": "cpu-1",
  "scope": "primehub"
}

* the scope field could be one of the ['public', 'primehub', 'group']
```

It follows our convention accepting a STDIN or with a real file by `--file` optional:

```
$ primehub apps create <<EOF
{
  "templateId": "code-server",
  "id": "code-server-26fcc",
  "displayName": "my-code-server-26fcc",
  "env": [
    {
      "name": "key1",
      "value": "value1"
    }
  ],
  "instanceType": "cpu-1",
  "scope": "primehub"
}
EOF
```

After the application created, it could be found at list:

```
$ primehub apps list
id:                code-server-26fcc
displayName:       my-code-server-26fcc
appVersion:        v3.9.2
appName:           code-server
appDefaultEnv:     None
appTemplate:
  name:            Code Server
  docLink:         https://github.com/cdr/code-server
  description:     Run VS Code on any machine anywhere and access it in the browser.
groupName:         phusers
instanceType:      cpu-1
instanceTypeSpec:
  name:            cpu-1
  displayName:     CPU 1 XD
  cpuLimit:        1
  memoryLimit:     2
  gpuLimit:        0
scope:             primehub
appUrl:            http://primehub-python-sdk.primehub.io/console/apps/code-server-26fcc
internalAppUrl:    http://app-code-server-26fcc:8080/console/apps/code-server-26fcc
svcEndpoints:      ['app-code-server-26fcc:8080']
env:               [{'name': 'key1', 'value': 'value1'}]
stop:              False
status:            Ready
message:           Deployment is ready
pods:              [{'logEndpoint': 'http://primehub-python-sdk.primehub.io/api/logs/pods/app-code-server-26fcc-765bf579c5-srcft'}]
```