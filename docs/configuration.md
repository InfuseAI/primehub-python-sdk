# Configuration

PrimeHub Python SDK provides the `primehub.PrimeHubConfig` class to set up itself. It works in this way:

1. load the default config path `~/.primehub/config.json` or load a specific path from the `config` argument
2. take settings from environment variables
3. overide from property setter

## Configuration file

The configuration file looks like:

```json
{
    "endpoint": "",
    "api-token": "",
    "group": {
        "id": "",
        "name": "",
        "displayName": "",
    }
}
```

* api-token and endpoint: they were generated from the PrimeHub Console
* group: the name of a group which is the active group to query with

## Environment Variables

There are three environment variables, they could be mapped to the field in the configuration file:

* PRIMEHUB_API_TOKEN maps to `api-token`
* PRIMEHUB_API_ENDPOINT maps to `endpoint`
* PRIMEHUB_GROUP maps to `group`

If a environment exists and not a blank value, it will override the value from the configuration file.

## Property Setter

We also provide a property setter to override one of the {endpoint, api-token, group}. They are available both of CLI and SDK:

```python
cfg = PrimeHubConfig()
cfg.group = 'set-a-different-group'
```

```bash
primehub --group set-a-different-group [command] ...
```

## Evaluation Order

We load variables in this order:

1. configuration file
2. environment variables
3. property

The configuration will override by environment variables and environment variables will override by property.