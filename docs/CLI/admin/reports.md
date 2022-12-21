
# <ADMIN> Primehub Reports

```
Usage: 
  primehub admin reports <command>

Get reports

Available Commands:
  download             Download a report by url
  list                 List reports

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### download

Download a report by url


```
primehub admin reports download <url>
```

* url: The report url.
 

* *(optional)* dest: The local path to save the report csv file




### list

List reports


```
primehub admin reports list
```
 

* *(optional)* page: the page of all data



 

## Examples

TBD: please write example for [reports]