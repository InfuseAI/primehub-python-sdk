
# Primehub Datasets

```
Usage: 
  primehub datasets <command>

Manage datasets

Available Commands:
  create               Create a datasets
  delete               Delete the dataset
  files-delete         delete files from the dataset
  files-download       download files from the dataset
  files-list           lists files of the dataset
  files-upload         upload files to the dataset
  get                  Get the dataset
  list                 List datasets
  update               Update a dataset

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

Create a datasets


```
primehub datasets create
```
 

* *(optional)* file: The file path of a datasets configuration




### delete

Delete the dataset


```
primehub datasets delete <dataset_id>
```

* dataset_id: the id of the dataset
 




### files-delete

delete files from the dataset


```
primehub datasets files-delete <dataset_id> <path>
```

* dataset_id: the name of the dataset
* path: the path of a file or a directory
 

* *(optional)* recursive: delete recursively, set it when the path is a directory




### files-download

download files from the dataset


```
primehub datasets files-download <dataset_id> <path> <dest>
```

* dataset_id: the name of the dataset
* path: the path of a file or a directory
* dest: the local path to save files
 

* *(optional)* recursive: copy recursively, set it when the path is a directory




### files-list

lists files of the dataset


```
primehub datasets files-list <dataset_id> <path>
```

* dataset_id: the name of the dataset
* path: the path of the dataset
 




### files-upload

upload files to the dataset


```
primehub datasets files-upload <dataset_id> <src> <path>
```

* dataset_id: the name of the dataset
* src: the path of a local file or local directory
* path: the path of the dataset
 

* *(optional)* recursive: copy recursively, set it when the source is a directory




### get

Get the dataset


```
primehub datasets get <dataset_id>
```

* dataset_id: the id of a dataset
 




### list

List datasets


```
primehub datasets list
```
 

* *(optional)* page: the page number as you can see in PrimeHub datasets UI




### update

Update a dataset


```
primehub datasets update <dataset_id>
```

* dataset_id: The id of a dataset
 

* *(optional)* file: The file path of a dataset configuration



 

## Examples

### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| id | required | string | the name of the dataset |
| tags | optional | object | dataset's tags |

*`tags` is a JSON array, e.g., `["dataset-tag-1", "dataset-tag-2"]`*

### Create a dataset

We could create a `test-dataset` dataset with tags `test-dataset-tag` and `training`:

```
$ primehub datasets create <<EOF
{
  "id": "test-dataset",
  "tags": ["test-dataset-tag", "training"]
}
EOF
```

### List datasets or get the dataset
After created a dataset, you could find it with `list` or `get` command

```
$ primehub datasets list

name          createdBy    updatedAt                 tags
------------  -----------  ------------------------  --------------------------------
test-dataset  phadmin      2021-12-06T12:48:38.293Z  ['test-dataset-tag', 'training']
```

```
$ primehub datasets get test-dataset
id:             test-dataset
name:           test-dataset
createdBy:      phadmin
createdAt:      2021-12-06T12:48:38.292Z
updatedAt:      2021-12-06T12:48:38.293Z
tags:           ['test-dataset-tag', 'training']
size:           0
```

### Update a dataset

We could update a dataset with new tags:

```
$ primehub datasets update test-dataset <<EOF
{
  "tags": ["deprecated"]
}
EOF

id:             test-dataset
name:           test-dataset
createdBy:      phadmin
createdAt:      2021-12-06T12:48:38.292Z
updatedAt:      2021-12-06T12:56:27.061Z
tags:           ['deprecated']
size:           0
```

### Delete a dataset

With `delete`, we could delete the whole dataset with its files.

```
$ primehub datasets delete test-dataset
id:             test-dataset
```

### Upload files to the dataset with given path

To upload a file or a directory to the dataset, `files-upload` command can help with it.

*Note: indicate `--recursive` options when upload directory*

We could upload a directory to the root path of the dataset

```
$ primehub datasets files-upload test-dataset ./test-dir / --recursive
[Uploading] ./test-dir/test.txt -> phfs:///datasets/test-dataset/test-dir/test.txt
[Uploading] ./test-dir/test-upload.txt -> phfs:///datasets/test-dataset/test-dir/test-upload.txt
success    phfs                                             file
---------  -----------------------------------------------  --------------------------
True       /datasets/test-dataset/test-dir/test.txt         ./test-dir/test.txt
True       /datasets/test-dataset/test-dir/test-upload.txt  ./test-dir/test-upload.txt
```

or upload a single file to the root path of the dataset

```
$ primehub datasets files-upload test-dataset ./test-upload.txt /
[Uploading] ./test-upload.txt -> phfs:///datasets/test-dataset/test-upload.txt
success    phfs                                    file
---------  --------------------------------------  ----------------------------------------------------
True       /datasets/test-dataset/test-upload.txt  ./test-upload.txt
```

You might upload sub-directory of the dataset

```
$ primehub datasets files-upload test-dataset ./test-upload.txt /test-dir
[Uploading] ./test-upload.txt -> phfs:///datasets/test-dataset/test-dir/test-upload.txt
success    phfs                                             file
---------  -----------------------------------------------  ----------------------------------------------------
True       /datasets/test-dataset/test-dir/test-upload.txt  ./test-upload.txt
```

### List files of the dataset with given path
We could use `files-list` to watch files of the dataset.

`files-list` requires `path` parameter, and `/` means the root path of the dataset.

```
$ primehub datasets files-list test-dataset /
name               size  lastModified
---------------  ------  ------------------------
test-upload.txt    1108  2021-12-09T04:03:12.000Z
test-dir/             0
```

You might go deeply into a sub-directory:

```
$ primehub datasets files-list test-dataset /test-dir
name               size  lastModified
---------------  ------  ------------------------
test-upload.txt    1108  2021-12-09T04:03:39.000Z
test.txt             13  2021-12-09T03:57:17.000Z
```

### Download files from the dataset with given path
`files-download` can help with downloading a file or a directory from the dataset.

*Note: indicate `--recursive` options when upload directory*

```
# download the whole dataset from root directory recursively
$ primehub datasets files-download test-dataset / ./local-dir --recursive

$ tree local-dir

local-dir
├── test-dir
│   ├── test-upload.txt
│   └── test.txt
└── test-upload.txt

1 directory, 3 files
```

### Delete files from the dataset with given path
We could delete a single file of the dataset or delete a specific directory of the dataset by `files-delete`.

*Note: indicate `--recursive` options when delete directory*

```
# delete a single file in the dataset
$ primehub datasets files-delete test-dataset /test-upload.txt
deleteFiles:    1

# delete a whole sub-directory of the dataset
$ primehub datasets files-delete test-dataset /test-dir --recursive
deleteFiles:    2
```