[Job Schedule](https://docs.primehub.io/docs/job-scheduling-feature) is a feature to make you create a job which is not
running immediately.

### Example: create a scheduled job

Here is an example copied from [Jobs](jobs.md):

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

Let's turn it to the schedule by adding `recurrence`

```
"recurrence": {"type": "daily", "cron": "0 4 * * *"}
```

It will be:

```
primehub schedules create <<EOF
{
    "instanceType": "cpu-1",
    "image": "base-notebook",
    "displayName": "Do my best job",
    "command": "echo \"great job\"",
    "recurrence": {"type": "daily", "cron": "0 4 * * *"}
}
EOF
```

Output:

```json
{
  "id": "schedule-moqib3",
  "displayName": "Do my best job",
  "recurrence": {
    "type": "daily",
    "cron": "0 4 * * *"
  },
  "invalid": false,
  "message": null,
  "command": "echo \"great job\"",
  "groupId": "2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376",
  "groupName": "phusers",
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
  "nextRunTime": null
}
```

### Example: submit a job from a schedule

Sometimes, the user want a scheduled job getting started right now! It could be done by jobs' `submit` command
with `--from <schedule-id>`

```
primehub jobs submit --from schedule-moqib3
```
```json
{
  "job": {
    "id": "job-202108040309-3f7bef"
  }
}
```