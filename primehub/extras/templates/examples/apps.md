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