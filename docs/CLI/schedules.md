
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
primehub create create
```
 



**Optional Arguments**

* file

 



#### Delete

Run a schedule by id


```
primehub delete delete <id>
```
**Required Arguments**
* id
 


 



#### Get

Get a schedule by id


```
primehub get get <id>
```
**Required Arguments**
* id
 


 



#### List

List schedules


```
primehub list list
```
 



**Optional Arguments**

* page

 



#### Update

Update a schedule by id


```
primehub update update <id>
```
**Required Arguments**
* id
 



**Optional Arguments**

* file

 


 

## Command Help

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
