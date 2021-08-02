
# Primehub Files

primehub files `<verb>` `[args]` `[flags]`


## Available Commands

* Download
* List



#### Download

Download shared files


```
primehub files download <path> <dest>
```

* path
* dest
 



Optional Arguments

* recursive

 



#### List

List shared files


```
primehub files list <path>
```

* path
 


 


 

## Command Help

```
Usage: 
  primehub files <command>

List and download shared files

Available Commands:
  download             Download shared files
  list                 List shared files

Options:
  -h, --help           Show the help

Global Options:
  --config CONFIG      the path of the config file
  --endpoint ENDPOINT  the endpoint to the PrimeHub GraphQL URL
  --token TOKEN        API Token generated from PrimeHub Console
  --group GROUP        override the active group

```