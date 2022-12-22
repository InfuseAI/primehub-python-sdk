
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


### Reports list and download

List reports

```
$ primehub admin reports list
primehub admin reports list --json | jq .
[
  {
    "id": "2022/12",
    "summaryUrl": "https://primehub-python-sdk.primehub.io/api/report/monthly/2022/12",
    "detailedUrl": "https://primehub-python-sdk.primehub.io/api/report/monthly/details/2022/12"
  }
]
```

Download a report by url:

```
$ primehub admin reports download https://primehub-python-sdk.primehub.io/api/report/monthly/details/2022/12
filename:       202212_details.csv
```

Download a report with `--dest` to change the download path:

```
$ primehub admin reports download https://primehub-python-sdk.primehub.io/api/report/monthly/2022/12 --dest foo/bar/202212.csv
filename:       /home/primehub/foo/bar/202212.csv
```