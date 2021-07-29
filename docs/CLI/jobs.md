

# Primehub Jobs

primehub jobs `<verb>` `[args]` `[flags]`



## Available Commands

- cancel
- get
- list
- logs
- rerun
- submit
- wait


#### Cancel

Cnacel a job by id 

```
primehub jobs cancel <id>
```


#### Get

Get a job by id 

```
primehub jobs get <id>
```


#### List

List jobs 

```
primehub jobs list 
```


#### Logs

Get job logs by id 

```
primehub jobs logs <id>
```


#### Rerun

Rerun a job by id 

```
primehub jobs rerun <id>
```


#### Submit

Submit a job 

```
primehub jobs submit 
```


#### Wait

Wait a job by id 

```
primehub jobs wait <id>
```

## Help
```
Usage: 
  primehub jobs <command>

Get a job or list jobs

Available Commands:
  cancel               Cnacel a job by id
  get                  Get a job by id
  list                 List jobs
  logs                 Get job logs by id
  rerun                Rerun a job by id
  submit               Submit a job
  wait                 Wait a job by id

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group
```
        