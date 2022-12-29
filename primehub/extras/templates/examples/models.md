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

### Example: register a model

List runs by experiment name

```
$ primehub models list-runs mnist
runId                               experimentId  status    startTime            endTime
--------------------------------  --------------  --------  -------------------  -------------------
b14a7d0b39d344af8cf9914d0616f27e               1  FINISHED  2022-12-27 18:25:58  2022-12-27 18:25:58
bd1694678bf2489f8de55d71bf9585db               1  FINISHED  2022-12-27 18:24:35  2022-12-27 18:24:35
3a3545ed3cb04c1dbe7b8e1392cbaf1a               1  FAILED    2022-12-27 18:24:23  2022-12-27 18:24:23
2fbd744173a44678ad9ca74bb3879d62               1  FAILED    2022-12-27 16:47:12  2022-12-27 16:47:12
```

List artifacts by run id

```
$ primehub models list-artifacts b14a7d0b39d344af8cf9914d0616f27e
path       is_dir      file_size
---------  --------  -----------
outputs    True
hello.txt  False             256
```

List artifacts by run id and specify search path

```
$ primehub models list-artifacts b14a7d0b39d344af8cf9914d0616f27e --path outputs
path                        is_dir      file_size
--------------------------  --------  -----------
outputs/.ipynb_checkpoints  True
outputs/bar                 True
outputs/foo                 True
outputs/test.txt            False              12
```

Register model

```
$ primehub models register model1 b14a7d0b39d344af8cf9914d0616f27e outputs/foo
name:                    model1
version:                 1
creation_timestamp:      1672161284579
last_updated_timestamp:  1672161284579
current_stage:           None
source:                  /project/foo/phapplications/mlflow-kvmdg/mlruns/1/b14a7d0b39d344af8cf9914d0616f27e/artifacts/outputs/foo
run_id:                  b14a7d0b39d344af8cf9914d0616f27e
status:                  READY
```

List the created model

```
$ primehub models list
name                creationTimestamp    lastUpdatedTimestamp    description      latestVersion
------------------  -------------------  ----------------------  -------------  ---------------
footest             2022-12-27 18:29:26  2022-12-27 18:29:26                                  1
created-by-graphql  2022-12-27 19:25:11  2022-12-27 19:43:08                                  2
abc                 2022-12-27 21:37:29  2022-12-28 00:45:09                                  5
model1              2022-12-28 01:14:44  2022-12-28 01:16:30                                  1
```
