### Example: create a deployment

We could use `create` to make a new model deployment. Here is an example when you are missing the required config file,
it shows you a *quickstart-iris* sample:

```
$ primehub deployments create
Deployment definition is required.


We take examples from:
https://docs.primehub.io/docs/model-deployment-tutorial-prepackaged-image

Definition example:
{
  "name": "quickstart-iris",
  "modelImage": "infuseai/sklearn-prepackaged:v0.1.0",
  "modelURI": "gs://seldon-models/sklearn/iris",
  "env": [],
  "metadata": {},
  "instanceType": "cpu-1",
  "replicas": 1,
  "updateMessage": "",
  "id": "quickstart-iris-cfmnh",
  "endpointAccessType": "public"
}
```

Let's create it:

```
$ primehub deployments create <<EOF
{
  "name": "quickstart-iris",
  "modelImage": "infuseai/sklearn-prepackaged:v0.1.0",
  "modelURI": "gs://seldon-models/sklearn/iris",
  "env": [],
  "metadata": {},
  "instanceType": "cpu-1",
  "replicas": 1,
  "updateMessage": "",
  "id": "quickstart-iris-cfmnh",
  "endpointAccessType": "public"
}
EOF
```

Our deployment was created, with the response:

```
id:                  quickstart-iris-cfmnh
name:                quickstart-iris
modelImage:          infuseai/sklearn-prepackaged:v0.1.0
imagePullSecret:     None
description:         None
replicas:            1
stop:                False
endpointAccessType:  public
endpointClients:     []
status:              Deploying
endpoint:            None
availableReplicas:   None
message:             None
pods:                []
```

### Example: query commands

List all deployments:

```
$ primehub deployments list
id                     name             modelImage                           description    stop    status    message
---------------------  ---------------  -----------------------------------  -------------  ------  --------  ----------------------------------------
quickstart-iris-cfmnh  quickstart-iris  infuseai/sklearn-prepackaged:v0.1.0                 False   Deployed  Deployment is deployed and available now
```

Get details by its id

```
$ primehub deployments get quickstart-iris-cfmnh
id:                  quickstart-iris-cfmnh
name:                quickstart-iris
modelImage:          infuseai/sklearn-prepackaged:v0.1.0
imagePullSecret:     None
description:         None
replicas:            1
stop:                False
endpointAccessType:  public
endpointClients:     []
status:              Deployed
endpoint:            http://primehub-python-sdk.primehub.io/deployment/quickstart-iris-cfmnh/api/v1.0/predictions
availableReplicas:   1
message:             Deployment is deployed and available now
pods:                [{'name': 'deploy-quickstart-iris-cfmnh-68889b97cc-8qgvf'}]
```

Check logs

```
$ primehub deployments logs quickstart-iris-cfmnh
2021-08-18 07:19:02,961 - seldon_core.app:load:81 - INFO:  Tracing branch is active
2021-08-18 07:19:02,966 - seldon_core.utils:setup_tracing:724 - INFO:  Initializing tracing
2021-08-18 07:19:03,164 - seldon_core.utils:setup_tracing:731 - INFO:  Using default tracing config
2021-08-18 07:19:03,164 - jaeger_tracing:_create_local_agent_channel:446 - INFO:  Initializing Jaeger Tracer with UDP reporter
2021-08-18 07:19:03,250 - jaeger_tracing:new_tracer:384 - INFO:  Using sampler ConstSampler(True)
2021-08-18 07:19:03,253 - jaeger_tracing:_initialize_global_tracer:436 - INFO:  opentracing.tracer initialized to <jaeger_client.tracer.Tracer object at 0x7fa79e142790>[app_name=Model]
2021-08-18 07:19:03,253 - seldon_core.app:load:86 - INFO:  Set JAEGER_EXTRA_TAGS []
2021-08-18 07:19:03,253 - Model:load_default:40 - INFO:  load
2021-08-18 07:19:03,253 - root:download:31 - INFO:  Copying contents of /mnt/models to local
2021-08-18 07:19:03,253 - Model:load_default:44 - INFO:  model file: /mnt/models/model.joblib
```

### Update deployments

We could use `update` command to make the deployment changed. The action could be easy with the `get` command
and `--json` output:

```
primehub deployments get quickstart-iris-cfmnh --json | jq
{
  "id": "quickstart-iris-cfmnh",
  "name": "quickstart-iris",
  "modelImage": "infuseai/sklearn-prepackaged:v0.1.0",
  "imagePullSecret": null,
  "description": null,
  "replicas": 1,
  "stop": false,
  "endpointAccessType": "public",
  "endpointClients": [],
  "status": "Deployed",
  "endpoint": "http://primehub-python-sdk.primehub.io/deployment/quickstart-iris-cfmnh/api/v1.0/predictions",
  "availableReplicas": 1,
  "message": "Deployment is deployed and available now",
  "pods": [
    {
      "name": "deploy-quickstart-iris-cfmnh-68889b97cc-8qgvf"
    }
  ]
}
```

We leave fields want to update:

```
$ primehub deployments update quickstart-iris-cfmnh <<EOF
{
  "description": "My First Deployment",
  "replicas": 2
}
EOF
```

Then checking the new status by `get`:

```
$ primehub deployments get quickstart-iris-cfmnh
id:                  quickstart-iris-cfmnh
name:                quickstart-iris
modelImage:          infuseai/sklearn-prepackaged:v0.1.0
imagePullSecret:     None
description:         My First Deployment
replicas:            2
stop:                False
endpointAccessType:  public
endpointClients:     []
status:              Deploying
endpoint:            http://primehub-python-sdk.primehub.io/deployment/quickstart-iris-cfmnh/api/v1.0/predictions
availableReplicas:   1
message:             Deployment is being deployed and not available now
pods:                [{'name': 'deploy-quickstart-iris-cfmnh-68889b97cc-8qgvf'}, {'name': 'deploy-quickstart-iris-cfmnh-68889b97cc-wxzs8'}]
```
