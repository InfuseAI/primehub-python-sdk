
# Primehub Jobs

primehub jobs `<verb>` `[args]` `[flags]`


## Available Commands

* Cancel
* Download-artifacts
* Get
* List
* List-artifacts
* Logs
* Rerun
* Submit
* Wait



#### Cancel

Cnacel a job by id


```
primehub cancel cancel <id>
```
**Required Arguments**
* id
 


 



#### Download-artifacts

Download artifacts


```
primehub download-artifacts download-artifacts <id> <path> <dest>
```
**Required Arguments**
* id
* path
* dest
 



**Optional Arguments**

* recursive

 



#### Get

Get a job by id


```
primehub get get <id>
```
**Required Arguments**
* id
 


 



#### List

List jobs


```
primehub list list
```
 



**Optional Arguments**

* page

 



#### List-artifacts

List artifacts of a job by id


```
primehub list-artifacts list-artifacts <id>
```
**Required Arguments**
* id
 


 



#### Logs

Get job logs by id


```
primehub logs logs <id>
```
**Required Arguments**
* id
 



**Optional Arguments**

* follow

* tail

 



#### Rerun

Rerun a job by id


```
primehub rerun rerun <id>
```
**Required Arguments**
* id
 


 



#### Submit

Submit a job


```
primehub submit submit
```
 



**Optional Arguments**

* file

* from

 



#### Wait

Wait a job by id


```
primehub wait wait <id>
```
**Required Arguments**
* id
 



**Optional Arguments**

* timeout

 


 

## Command Help

Usage: 
  primehub jobs <command>

Get a job or list jobs

Available Commands:
  cancel               Cnacel a job by id
  download-artifacts   Download artifacts
  get                  Get a job by id
  list                 List jobs
  list-artifacts       List artifacts of a job by id
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
