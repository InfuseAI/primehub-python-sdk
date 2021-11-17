### Fields for submitting

| field | required | type | description |
| --- | --- | --- | --- |
| displayName | required | string | display name |
| instanceType | required | string | instance type which allocates resources for the job |
| image | required | string | image which the job run bases on |
| command | required | string | sequential commands of the job context |
| activeDeadlineSeconds | optional | int | a running job will be cancelled after this time period (in seconds) |

### Submit a job

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
recurrence:     None
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

#### Note
There are a few **[limitations](https://docs.primehub.io/docs/job-submission-feature#limitation)**, e.g., maximum execution time, log preservation.

### Check job status

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
recurrence:     None
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

### Check log messages with `logs` command

```
primehub jobs logs job-202108180756-pqihgl
```

```
great job
Artifacts: no artifact found
```

### Job Artifacts

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
