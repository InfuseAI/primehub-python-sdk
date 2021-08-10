
# Primehub Deployments

```
Usage: 
  primehub deployments <command>

Get a deployment or list deployments

Available Commands:
  create               Create a deployment
  delete               Delete a deployment by id
  get                  Get a deployment by id
  get-history          Get history of a deployment by id
  list                 List deployments
  logs                 Get deployment logs by id
  start                Start a deployment by id
  stop                 Stop a deployment by id
  update               Update a deployment by id
  wait                 Wait a deployment to complete

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group

```


### create

Create a deployment


```
primehub deployments create
```
 

* *(optional)* file: The file path of deployment configurations




### delete

Delete a deployment by id


```
primehub deployments delete <id>
```

* id: The deployment id
 




### get

Get a deployment by id


```
primehub deployments get <id>
```

* id: The deployment id
 




### get-history

Get history of a deployment by id


```
primehub deployments get-history <id>
```

* id: The deployment id
 




### list

List deployments


```
primehub deployments list
```
 




### logs

Get deployment logs by id


```
primehub deployments logs <id>
```

* id: The job id
 

* *(optional)* pod: The target pod to log

* *(optional)* follow: Wait for additional logs to be appended

* *(optional)* tail: Show last n lines




### start

Start a deployment by id


```
primehub deployments start <id>
```

* id: The deployment id
 




### stop

Stop a deployment by id


```
primehub deployments stop <id>
```

* id: The deployment id
 




### update

Update a deployment by id


```
primehub deployments update <id>
```

* id
 

* *(optional)* file: The file path of deployment configurations




### wait

Wait a deployment to complete


```
primehub deployments wait <id>
```

* id: The job id
 

* *(optional)* timeout: The timeout in second



 

## Examples

TBD: please write example for [deployments]