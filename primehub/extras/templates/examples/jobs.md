### Example: submit a job

Using `submit` to create a job, it needs the job definition. We could give the job definition either `stdin` or `--file`
flag.

```
primehub jobs submit <<EOF
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
{"id": "job-202108030945-18h0zi", "displayName": "Do my best job", "cancel": false, "command": "echo \"great job\"", "groupId": "2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376", "groupName": "phusers", "schedule": null, "image": "base-notebook", "instanceType": {"id": "cpu-1", "name": "cpu-1", "displayName": "CPU 1", "cpuLimit": 0.5, "memoryLimit": 2, "gpuLimit": 0}, "userId": "a7db12dc-04fa-419c-9cd7-af768575a871", "userName": "phadmin", "phase": "Pending", "reason": null, "message": null, "createTime": "2021-08-03T09:45:44Z", "startTime": null, "finishTime": null}
```

### Example: check job status

* `list` and `get` could get jobs status

```
primehub jobs get job-202108030945-18h0zi
```

```json
{
  "id": "job-202108030945-18h0zi",
  "displayName": "Do my best job",
  "cancel": null,
  "command": "echo \"great job\"",
  "groupId": "2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376",
  "groupName": "phusers",
  "schedule": null,
  "image": "base-notebook",
  "instanceType": {
    "id": "cpu-1",
    "name": "cpu-1",
    "displayName": "CPU 1",
    "cpuLimit": 0.5,
    "memoryLimit": 2,
    "gpuLimit": 0
  },
  "userId": "a7db12dc-04fa-419c-9cd7-af768575a871",
  "userName": "phadmin",
  "phase": "Succeeded",
  "reason": "PodSucceeded",
  "message": "Job completed",
  "createTime": "2021-08-03T09:45:44Z",
  "startTime": "2021-08-03T09:45:47Z",
  "finishTime": "2021-08-03T09:45:48Z"
}
```

check log messages with `logs` command

```
primehub jobs logs job-202108030945-18h0zi
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
primehub jobs submit <<EOF
{
    "instanceType": "cpu-1",
    "image": "base-notebook",
    "displayName": "Make artifacts",
    "command": "mkdir -p /home/jovyan/artifacts; echo \"show me\" > /home/jovyan/artifacts/README"
}
EOF
```

Output:

```json
{
  "id": "job-202108040123-yoeymt",
  "displayName": "Make artifacts",
  "cancel": null,
  "command": "mkdir -p /home/jovyan/artifacts; echo \"show me\" > /home/jovyan/artifacts/README",
  "groupId": "2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376",
  "groupName": "phusers",
  "schedule": null,
  "image": "base-notebook",
  "instanceType": {
    "id": "cpu-1",
    "name": "cpu-1",
    "displayName": "CPU 1",
    "cpuLimit": 1,
    "memoryLimit": 2,
    "gpuLimit": 0
  },
  "userId": "a7db12dc-04fa-419c-9cd7-af768575a871",
  "userName": "phadmin",
  "phase": "Succeeded",
  "reason": "PodSucceeded",
  "message": "Job completed",
  "createTime": "2021-08-04T01:23:10Z",
  "startTime": "2021-08-04T01:23:29Z",
  "finishTime": "2021-08-04T01:23:30Z"
}
```

Using `list-artifacts` and `download-artifacts` get check and get files:

```
primehub jobs list-artifacts job-202108040123-yoeymt 
```

```json
{
  "prefix": "groups/phusers/jobArtifacts/job-202108040123-yoeymt",
  "items": [
    {
      "name": "README",
      "size": 8,
      "lastModified": "2021-08-04T01:23:29.834Z"
    }
  ]
}
```

Saving the README file to the current directory `.`

```
primehub jobs download-artifacts job-202108040123-yoeymt README .
```
```
$ cat README
show me
```