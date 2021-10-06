The `list` action will show you each template that is registered to the PrimeHub

```
primehub apptemplates list
```

```
id:             code-server
name:           Code Server
version:        v3.9.2
description:    Run VS Code on any machine anywhere and access it in the browser.
docLink:        https://github.com/cdr/code-server
image:          codercom/code-server:3.9.2

id:             label-studio
name:           Label Studio
version:        1.1.0
description:    Label Studio is an open source data labeling tool for labeling and exploring multiple types of data. You can perform many different types of labeling for many different data formats.
docLink:        https://labelstud.io/guide/
image:          heartexlabs/label-studio:1.1.0

id:             matlab
name:           Matlab
version:        r2020b
description:    MATLAB is a programming platform designed for engineers and scientists. The MATLAB Deep Learning Container provides algorithms, pretrained models, and apps to create, train, visualize, and optimize deep neural networks.
docLink:        https://ngc.nvidia.com/catalog/containers/partners:matlab/tags
image:          nvcr.io/partners/matlab:r2020b

id:             mlflow
name:           MLflow
version:        v1.9.1
description:    MLflow is an open source platform to manage the ML lifecycle, including experimentation, reproducibility, deployment, and a central model registry.
docLink:        https://www.mlflow.org/docs/1.9.1/index.html
image:          larribas/mlflow:1.9.1

id:             streamlit
name:           Streamlit
version:        v0.79.0
description:    Streamlit turns data scripts into shareable web apps in minutes. All in Python. All for free. No front‑end experience required.
docLink:        https://docs.primehub.io/docs/primehub-app-builtin-streamlit
image:          infuseai/streamlit:v0.79.0
```

You could get one of them with `get` action and the id of a template:

```
primehub apptemplates get code-server
```


```
id:             code-server
name:           Code Server
version:        v3.9.2
description:    Run VS Code on any machine anywhere and access it in the browser.
docLink:        https://github.com/cdr/code-server
image:          codercom/code-server:3.9.2
```