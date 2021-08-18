
# Primehub Jobs

```
Usage: 
  primehub jobs <command>

Get a job or list jobs

Available Commands:
  cancel               Cancel a job by id
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
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### cancel

Cancel a job by id


```
primehub jobs cancel <id>
```

* id: The job id
 




### download-artifacts

Download artifacts


```
primehub jobs download-artifacts <id> <path> <dest>
```

* id: The job id
* path: The path of job artifacts
* dest: The local path to save artifacts
 

* *(optional)* recursive




### get

Get a job by id


```
primehub jobs get <id>
```

* id: The job id
 




### list

List jobs


```
primehub jobs list
```
 

* *(optional)* page: The page number as you can see in PrimeHub Jobs UI




### list-artifacts

List artifacts of a job by id


```
primehub jobs list-artifacts <id>
```

* id: The job id
 




### logs

Get job logs by id


```
primehub jobs logs <id>
```

* id: The job id
 

* *(optional)* follow: Wait for additional logs to be appended

* *(optional)* tail: Show last n lines




### rerun

Rerun a job by id


```
primehub jobs rerun <id>
```

* id: The job id
 




### submit

Submit a job


```
primehub jobs submit
```
 

* *(optional)* file: The file path of job configurations

* *(optional)* from: The schedule id to submit as a job




### wait

Wait a job by id


```
primehub jobs wait <id>
```

* id: The job id
 

* *(optional)* timeout: The timeout in second



 

## Examples

### Example: submit a job

Using `submit` to create a job, it needs the job definition. We could give the job definition either `stdin` or `--file`
flag.

```
$ primehub jobs submit <<EOF
{
    "instanceType": "cpu-1",
    "image": "base-notebook",
    "displayName": "Do my best job",
    "command": "echo \"great job\""
}
EOF
```

After submitted, it will show the output:

```
id:             job-202108180756-pqihgl
displayName:    Do my best job
cancel:         False
command:        echo "great job"
groupId:        2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376
groupName:      phusers
schedule:       None
image:          base-notebook
instanceType:
  id:           cpu-1
  name:         cpu-1
  displayName:  CPU 1
  cpuLimit:     0.5
  memoryLimit:  2
  gpuLimit:     0
userId:         a7db12dc-04fa-419c-9cd7-af768575a871
userName:       phadmin
phase:          Pending
reason:         None
message:        None
createTime:     2021-08-18T07:56:48Z
startTime:      None
finishTime:     None 
```

### Example: check job status

* `list` and `get` could get jobs status

```
$ primehub jobs get job-202108180756-pqihgl
```

```
id:             job-202108180756-pqihgl
displayName:    Do my best job
cancel:         None
command:        echo "great job"
groupId:        2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376
groupName:      phusers
schedule:       None
image:          base-notebook
instanceType:
  id:           cpu-1
  name:         cpu-1
  displayName:  CPU 1
  cpuLimit:     0.5
  memoryLimit:  2
  gpuLimit:     0
userId:         a7db12dc-04fa-419c-9cd7-af768575a871
userName:       phadmin
phase:          Succeeded
reason:         PodSucceeded
message:        Job completed
createTime:     2021-08-18T07:56:48Z
startTime:      2021-08-18T07:56:58Z
finishTime:     2021-08-18T07:56:59Z
```

check log messages with `logs` command

```
primehub jobs logs job-202108180756-pqihgl
```

```
great job
Artifacts: no artifact found
```

### Example: Artifacts

[Job Artifacts](https://docs.primehub.io/docs/job-artifact-feature) is a feature to keep a job's output files to the
shared spaces. Any files in the directory `/home/jovyan/artifacts` will upload
to [Shared Files](https://docs.primehub.io/docs/shared-files).

Let's start it with a new job:

```
$ primehub jobs submit <<EOF
{
    "instanceType": "cpu-1",
    "image": "base-notebook",
    "displayName": "Make artifacts",
    "command": "mkdir -p /home/jovyan/artifacts; echo \"show me\" > /home/jovyan/artifacts/README"
}
EOF
```

Using `list-artifacts` and `download-artifacts` get check and get files:

```
$ primehub jobs list-artifacts job-202108180759-z2legx
name      size  lastModified
------  ------  ------------------------
README       8  2021-08-18T07:59:19.642Z
```

Saving the README file to the current directory `.`

```
$ primehub jobs download-artifacts job-202108180759-z2legx README .
```
```
$ cat README
show me
```