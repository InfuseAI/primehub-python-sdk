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

```
$ primehub datasets files-upload test-dir test-dataset --recursive
[Uploading] test-dir/test-file.txt -> phfs:///datasets/test-dataset/test-dir/test-file.txt
success    phfs                                           file
---------  ---------------------------------------------  ----------------------
True       /datasets/test-dataset/test-dir/test-file.txt  test-dir/test-file.txt

$ primehub datasets files-upload test-upload-file.txt test-dataset/test-dir
[Uploading] /tmp/test-upload-file.txt -> phfs:///datasets/test-dataset/test-dir/test-upload-file.txt
success    phfs                                                  file
---------  ----------------------------------------------------  ---------------------------------------------------------
True       /datasets/test-dataset/test-dir/test-upload-file.txt  /tmp/test-upload-file.txt
```

### List files of the dataset with given path
We could use `files-list` to watch files of the dataset.

`files-list` requires a `path` parameter, and it always starts with the name of the dataset:

```
$ primehub datasets files-list test-dataset
name                    size  lastModified
--------------------  ------  ------------------------
.dataset                 123  2021-12-06T12:56:28.000Z
test-upload-file.txt      12  2021-12-06T15:10:15.000Z
test-dir/                  0
```

You might go deeply into a sub-directory:

```
$ primehub datasets files-list test-dataset/test-dir
name                    size  lastModified
--------------------  ------  ------------------------
test-file.txt             39  2021-12-06T15:09:59.000Z
test-upload-file.txt      12  2021-12-06T15:12:41.000Z
```

### Download files from the dataset with given path
`files-download` can help with downloading a file or a directory from the dataset.

*Note: indicate `--recursive` options when upload directory*

```
$ primehub datasets files-download test-dataset local-dir --recursive

$ tree local-dir
local-dir
└── test-dataset
    ├── test-dir
    │   ├── test-file.txt
    │   └── test-upload-file.txt
    └── test-upload-file.txt

2 directories, 3 files
```
