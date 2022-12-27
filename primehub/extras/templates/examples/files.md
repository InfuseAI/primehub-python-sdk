We could use `list` to watch files or directory remotely.

`list` requires a `path` parameter, it always starts with `/`:

```
$ primehub files list /
name             size  lastModified    phfsUri
-------------  ------  --------------  ---------------------
jobArtifacts/       0                  phfs:///jobArtifacts/
```

You might go deeply into a sub-directory:

```
$ primehub files list /jobArtifacts/job-202107290838-aoq173/
name          size  lastModified    phfsUri
----------  ------  --------------  ------------------
.metadata/       0                  phfs:///.metadata/
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
