
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
