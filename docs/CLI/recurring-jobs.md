
# Primehub Recurring-jobs

```
Usage: 
  primehub recurring-jobs <command>

Manage recurring jobs

Available Commands:
  create               Create a recurring job
  delete               Delete a recurring job by id
  get                  Get a recurring job by id
  list                 List recurring jobs
  update               Update a recurring job by id

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

Create a recurring job


```
primehub recurring-jobs create
```
 

* *(optional)* file: The file path of recurring job configurations




### delete

Delete a recurring job by id


```
primehub recurring-jobs delete <id>
```

* id: The recurring job id
 




### get

Get a recurring job by id


```
primehub recurring-jobs get <id>
```

* id: The recurring job id
 




### list

List recurring jobs


```
primehub recurring-jobs list
```
 

* *(optional)* page: The page number as you can see in PrimeHub RecurringJobs UI




### update

Update a recurring job by id


```
primehub recurring-jobs update <id>
```

* id
 

* *(optional)* file: The file path of recurring job configurations



 

## Examples

### Recurring Jobs
[Recurring jobs](https://docs.primehub.io/docs/job-scheduling-feature)
is a feature to make you create a job which is not running immediately.

### Fields for creating

| field | required | type | description |
| --- | --- | --- | --- |
| displayName | required | string | display name |
| instanceType | required | string | instance type which allocates resources for the job |
| image | required | string | image which the job run bases on |
| command | required | string | sequential commands of the job context |
| recurrence | required | object | rule of trigger recurrence |
| activeDeadlineSeconds | optional | int | a running job will be cancelled after this time period (in seconds) |

#### Recurrence options
We can select one of presets of rules or customize a rule based on [Cron](https://en.wikipedia.org/wiki/Cron) syntax.
e.g., `0 4 * * *` represents 4 AM every day.

| Options	| Description |
| --- | --- |
| on-demand | trigger jobs by user request |
| daily | a preset; trigger a job at 4 AM everyday |
| weekly | a preset; trigger a job at 4 AM on Sunday every week |
| monthly | a preset; trigger a job at 4 AM on 1st every month |
| custom |	customize the rule of the trigger recurrence |

Only with "custom' type, we need to specify corresponding cron column.

Format examples:
```
"recurrence": {"type": "daily"}
"recurrence": {"type": "on-demand", "cron": ""}
"recurrence": {"type": "custom", "cron": "45 23 * * 6"}   # at 23:45 (11:45 PM) every Saturday
```

### Create a recurring job

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

Let's turn it to the recurring job by adding `recurrence`

```
"recurrence": {"type": "daily", "cron": ""}
```

It will be:

```
primehub recurring_jobs create <<EOF
{
    "instanceType": "cpu-1",
    "image": "base-notebook",
    "displayName": "Do my best job",
    "command": "echo \"great job\"",
    "recurrence": {"type": "daily", "cron": ""}
}
EOF
```

Output:

```
id:             recurrence-tdcfta
displayName:    Do my best job
recurrence:
  type:         daily
  cron:         None
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

### Submit a job from a recurring job

Sometimes, the user want a recurring job getting started right now! It could be done by jobs' `submit` command
with `--from <recurring-job-id>`

```
$ primehub jobs submit --from recurrence-tdcfta
```
```
job:
  id:           job-202108180808-8tnk6z
```