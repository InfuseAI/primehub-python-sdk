

# Primehub Schedules

primehub schedules `<verb>` `[args]` `[flags]`



## Available Commands

- create
- delete
- get
- list
- update


#### Create

Create a schedule 

```
primehub schedules create 
```


#### Delete

Run a schedule by id (`--yes-i-really-mean-it` is required)

```
primehub schedules delete <id>
```


#### Get

Get a schedule by id 

```
primehub schedules get <id>
```


#### List

List schedules 

```
primehub schedules list 
```


#### Update

Update a schedule by id 

```
primehub schedules update <id>
```

## Help
```
Usage: 
  primehub schedules <command>

Get a schedule or list schedules

Available Commands:
  create               Create a schedule
  delete               Run a schedule by id
  get                  Get a schedule by id
  list                 List schedules
  update               Update a schedule by id

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group
```
        