
# Primehub Schedules

primehub schedules `<verb>` `[args]` `[flags]`


## Available Commands

* Create
* Delete
* Get
* List
* Update



#### Create

Create a schedule


```
primehub schedules create
```
 



Optional Arguments

* file

 



#### Delete

Run a schedule by id


```
primehub schedules delete <id>
```

* id
 


 



#### Get

Get a schedule by id


```
primehub schedules get <id>
```

* id
 


 



#### List

List schedules


```
primehub schedules list
```
 



Optional Arguments

* page

 



#### Update

Update a schedule by id


```
primehub schedules update <id>
```

* id
 



Optional Arguments

* file

 


 

## Command Help

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