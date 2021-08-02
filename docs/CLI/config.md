
# Primehub Config

primehub config `<verb>` `[args]` `[flags]`


## Available Commands

* Set-endpoint
* Set-group
* Set-token



#### Set-endpoint

set endpoint and save to the config file


```
primehub config set-endpoint <endpoint>
```

* endpoint
 


 



#### Set-group

set group and save to the config file


```
primehub config set-group <group>
```

* group
 


 



#### Set-token

set token and save to the config file


```
primehub config set-token <token>
```

* token
 


 


 

## Command Help

```
Usage: 
  primehub config <command>

Update the settings of PrimeHub SDK

Available Commands:
  set-endpoint         set endpoint and save to the config file
  set-group            set group and save to the config file
  set-token            set token and save to the config file

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group

```