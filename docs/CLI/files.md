
# Primehub Files

```
Usage: 
  primehub files <command>

List and download shared files

Available Commands:
  delete               delete shared files
  download             Download shared files
  list                 List shared files
  upload               Upload shared files

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      Change the path of the config file (Default: ~/.primehub/config.json)
  --endpoint ENDPOINT  Override the GraphQL API endpoint
  --token TOKEN        Override the API Token
  --group GROUP        Override the current group
  --json               Output the json format (output human-friendly format by default)

```


### delete

delete shared files


```
primehub files delete <path>
```

* path: The path of file or folder
 

* *(optional)* recursive: Delete recursively, it works when a path is a directory.




### download

Download shared files


```
primehub files download <path> <dest>
```

* path: The path of file or folder
* dest: The local path to save artifacts
 

* *(optional)* recursive




### list

List shared files


```
primehub files list <path>
```

* path: The path to list
 




### upload

Upload shared files


```
primehub files upload <src> <path>
```

* src: The local path to save artifacts
* path: The path of file or folder
 

* *(optional)* recursive



 

## Examples

We could use `list` to watch files or directory remotely.

`list` requires a `path` parameter, it always starts with `/`:

```
$ primehub files list /
name             size  lastModified
-------------  ------  --------------
jobArtifacts/       0
```

You might go deeply into a sub-directory:

```
$ primehub files list /jobArtifacts/job-202107290838-aoq173/
name          size  lastModified
----------  ------  --------------
.metadata/       0
```

Then `download` a file directly or a directory with `--recursive` options

```
$ primehub files download /jobArtifacts/job-202107290838-aoq173 ./my-download --recursive
```

```
./my-download
└── job-202107290838-aoq173
    └── .metadata

1 directory, 1 file
```

Uses `upload` to upload a file or a directory with `--recursive` options.

*Note: it follows shell `cp -R` manner when upload a directory*
> If the source_file ends in a /, the contents of the directory are copied rather than the directory itself.

```
$ primehub files upload ./my-download /jobArtifacts/job-202107290838-aoq173 --recursive
[Uploading] ./my-download/job-202107290838-aoq173/.metadata -> phfs:///jobArtifacts/job-202107290838-aoq173/my-download/job-202107290838-aoq173/.metadata
success    phfs                                                                                 file
---------  -----------------------------------------------------------------------------------  -----------------------------------------------
True       /jobArtifacts/job-202107290838-aoq173/my-download/job-202107290838-aoq173/.metadata  ./my-download/job-202107290838-aoq173/.metadata
```

```
$ primehub files upload ./my-download/ /jobArtifacts/job-202107290838-aoq173 --recursive
[Uploading] ./my-download/job-202107290838-aoq173/.metadata -> phfs:///jobArtifacts/job-202107290838-aoq173/job-202107290838-aoq173/.metadata
success    phfs                                                                     file
---------  -----------------------------------------------------------------------  -----------------------------------------------
True       /jobArtifacts/job-202107290838-aoq173/job-202107290838-aoq173/.metadata  ./my-download/job-202107290838-aoq173/.metadata
```

Uses `delete` to delete a file or a directory with `--recursive` options.

```
$ primehub files delete /jobArtifacts/job-202107290838-aoq173 --recursive
deleteFiles:    3
```