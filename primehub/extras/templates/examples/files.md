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

Uses `delete` to delete a file or a directory with `--recursive` options.

```
$ primehub files delete /jobArtifacts/job-202107290838-aoq173 --recursive
```
