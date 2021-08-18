
# Primehub Schedules

```
Usage: 
  primehub schedules <command>

Get a schedule or list schedules

Available Commands:
  create               Create a schedule
  delete               Delete a schedule by id
  get                  Get a schedule by id
  list                 List schedules
  update               Update a schedule by id

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### create

Create a schedule


```
primehub schedules create
```
 

* *(optional)* file: The file path of schedule configurations




### delete

Delete a schedule by id


```
primehub schedules delete <id>
```

* id: The schedule id
 




### get

Get a schedule by id


```
primehub schedules get <id>
```

* id: The schedule id
 




### list

List schedules


```
primehub schedules list
```
 

* *(optional)* page: The page number as you can see in PrimeHub Schedules UI




### update

Update a schedule by id


```
primehub schedules update <id>
```

* id
 

* *(optional)* file: The file path of schedule configurations



 

## Examples

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

```
id:             schedule-tdcfta
displayName:    Do my best job
recurrence:
  type:         daily
  cron:         0 4 * * *
invalid:        False
message:        None
command:        echo "great job"
groupId:        2b080113-e2f1-4b1b-a6ef-eb0ca5e2f376
groupName:      phusers
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
nextRunTime:    None
```

### Example: submit a job from a schedule

Sometimes, the user want a scheduled job getting started right now! It could be done by jobs' `submit` command
with `--from <schedule-id>`

```
$ primehub jobs submit --from schedule-tdcfta
```
```
job:
  id:           job-202108180808-8tnk6z
```