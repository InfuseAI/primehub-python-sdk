
# Primehub Notebooks

```
Usage: 
  primehub notebooks <command>

Get notebooks logs

Available Commands:
  logs                 Get notebooks logs

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### logs

Get notebooks logs


```
primehub notebooks logs
```
 

* *(optional)* follow: Wait for additional logs to be appended

* *(optional)* tail: Show last n lines



 

## Examples

See log messages from the user's notebook

```
primehub notebooks logs
```

```
Set username to: jovyan
usermod: no changes
Changing ownership of /datasets/kaggle to 1000:100 with options ''
Changing ownership of /phfs to 1000:100 with options ''
Changing ownership of /home/jovyan to 1000:100 with options ''
Granting jovyan sudo access and appending /opt/conda/bin to sudo PATH
Executing the command: jupyter labhub --ip=0.0.0.0 --port=8888 --NotebookApp.default_url=/lab
[W 2021-08-03 10:01:20.065 SingleUserLabApp configurable:190] Config option `open_browser` not recognized by `SingleUserLabApp`.  Did you mean one of: `browser, expose_app_in_browser`?
[WARNING 2021-08-03 10:01:21.567 SingleUserLabApp zmqhandlers:275] Couldn't authenticate WebSocket connection
[WARNING 2021-08-03 10:01:21.601 SingleUserLabApp log:181] 403 GET /user/phadmin/api/kernels/cc295b85-35dc-4c6b-b8fd-ac3885224738/channels?session_id=be318bb4-b241-4b57-83a3-63f10b746ba8 (@36.225.16.122) 35.68ms
```

### Notes

If the notebook has not been ready, you might get status message:

```
{"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"container \"notebook\" in pod \"jupyter-phadmin\" is waiting to start: PodInitializing","reason":"BadRequest","code":400}
```