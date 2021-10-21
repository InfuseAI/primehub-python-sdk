
# Primehub Models

```
Usage: 
  primehub models <command>

Manage models

Available Commands:
  deploy               Deploy the model version to the speific deployment
  get                  Get the model
  get-version          Get a version of the model
  list                 List models
  list-versions        List versions of the model

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### deploy

Deploy the model version to the speific deployment


```
primehub models deploy <model> <version> <deploy_id>
```

* model: The model name
* version: Verson number
* deploy_id: Deployment id
 




### get

Get the model


```
primehub models get <name>
```

* name: The model name
 




### get-version

Get a version of the model


```
primehub models get-version <model> <version>
```

* model: The model name
* version: Verson number
 




### list

List models


```
primehub models list
```
 




### list-versions

List versions of the model


```
primehub models list-versions <model>
```

* model: The model name
 



 

## Examples

### Example: query commands

List all models:

```
$ primehub models list
name    creationTimestamp    lastUpdatedTimestamp    description      latestVersion
------  -------------------  ----------------------  -------------  ---------------
foo     2021-10-15 16:04:29  2021-10-19 21:31:08                                  2
bar     2021-10-14 12:16:26  2021-10-20 16:39:02                                  5
```

Get details by model name

```
$ primehub models get foo
mlflow:
  trackingUri:  http://app-mlflow-045jg:5000
  uiUrl:        https://primehub-python-sdk.primehub.io/console/apps/mlflow-045jg
model:
  name:         foo
  creationTimestamp:2021-10-15 16:04:29
  lastUpdatedTimestamp:2021-10-19 21:31:08
  description:  None
  latestVersions:[{'name': 'foo', 'version': '2'}]
versions:
  -
  name:                  foo
  version:               1
  creationTimestamp:     2021-10-15 16:04:29
  lastUpdatedTimestamp:  2021-10-15 16:04:29
  deployedBy:            [{'id': 'deployment-foo-dhpqt', 'name': 'deployment-foo'}]
  -
  name:                  foo
  version:               2
  creationTimestamp:     2021-10-19 21:31:08
  lastUpdatedTimestamp:  2021-10-19 21:31:08
  deployedBy:            []
```

List all versions of a model

```
$ primehub models list-versions foo
name      version  creationTimestamp    lastUpdatedTimestamp    deployedBy
------  ---------  -------------------  ----------------------  ----------------------------------------------------------
foo             1  2021-10-15 16:04:29  2021-10-15 16:04:29     [{'id': 'deployment-foo-dhpqt', 'name': 'deployment-foo'}]
foo             2  2021-10-19 21:31:08  2021-10-19 21:31:08     []
```

Get version details by model name and version number

```
$ primehub models get-version foo 1
name:                  foo
version:               1
creationTimestamp:     2021-10-15 16:04:29
lastUpdatedTimestamp:  2021-10-15 16:04:29
deployedBy:            [{'id': 'deployment-foo-dhpqt', 'name': 'deployment-foo'}]
run:
  info:
    runId:        8e3c1e566ad54629a5762b9dd0b74a27
    experimentId: 1
    status:       FINISHED
    startTime:    2021-10-15 16:01:58
    endTime:      2021-10-15 16:02:20
    artifactUri:  /project/foo/phapplications/mlflow-045jg/mlruns/1/8e3c1e566ad54629a5762b9dd0b74a27/artifacts
    lifecycleStage:active
  data:
    metrics:
      key          value  timestamp              step
      --------  --------  -------------------  ------
      loss      1.51079   2021-10-15 16:02:19       2
      accuracy  0.954383  2021-10-15 16:02:19       2
    params:
      key                    value
      ---------------------  -------
      batch_size             None
      class_weight           None
      epochs                 3
      initial_epoch          0
      max_queue_size         10
      opt_amsgrad            False
      opt_beta_1             0.9
      opt_beta_2             0.999
      opt_decay              0.0
      opt_epsilon            1e-07
      opt_learning_rate      0.001
      opt_name               Adam
      sample_weight          None
      shuffle                True
      steps_per_epoch        None
      use_multiprocessing    False
      validation_batch_size  None
      validation_freq        1
      validation_split       0.0
      validation_steps       None
      workers                1
```

### Example: deploy a model to existing deployments

We could deploy the specific model and version to an existing deployment by using `deploy` command

```
$ primehub models deploy foo 1 deployment-foo-dhpqt
id:                  deployment-foo-dhpqt
name:                deployment-foo
modelImage:          infuseai/tensorflow2-prepackaged:v0.2.0
imagePullSecret:     None
description:         None
replicas:            1
stop:                False
endpointAccessType:  public
endpointClients:     []
status:              Deploying
endpoint:            https://primehub-python-sdk.primehub.io/deployment/deployment-foo-dhpqt/api/v1.0/predictions
availableReplicas:   None
message:             Deployment is being deployed and not available now
pods:                [{'name': 'deploy-deployment-foo-dhpqt-6bcd77b854-lwcz8'}]
```