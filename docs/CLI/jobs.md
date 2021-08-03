
# Primehub Jobs

```
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

```


### Cancel

Cnacel a job by id


```
primehub jobs cancel <id>
```

* id
 


 



### Download-artifacts

Download artifacts


```
primehub jobs download-artifacts <id> <path> <dest>
```

* id
* path
* dest
 



Optional Arguments

* recursive

 



### Get

Get a job by id


```
primehub jobs get <id>
```

* id
 


 



### List

List jobs


```
primehub jobs list
```
 



Optional Arguments

* page

 



### List-artifacts

List artifacts of a job by id


```
primehub jobs list-artifacts <id>
```

* id
 


 



### Logs

Get job logs by id


```
primehub jobs logs <id>
```

* id
 



Optional Arguments

* follow

* tail

 



### Rerun

Rerun a job by id


```
primehub jobs rerun <id>
```

* id
 


 



### Submit

Submit a job


```
primehub jobs submit
```
 



Optional Arguments

* file

* from

 



### Wait

Wait a job by id


```
primehub jobs wait <id>
```

* id
 



Optional Arguments

* timeout

 


 
