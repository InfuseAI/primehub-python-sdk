
# Primehub Files

```
Usage: 
  primehub files <command>

List and download shared files

Available Commands:
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
$ tree ./my-download
./my-download
`-- job-202107290838-aoq173
```

Uses `upload` to upload a file or a directory with `--recursive` options.

```
$ primehub files upload ./my-download /jobArtifacts/job-202107290838-aoq173 --recursive
```