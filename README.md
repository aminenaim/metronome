# Jackiebot

Version 1.3.1

This script parse STRI edt from pdf to ics format.

It uses python 3.8 and higher version

## Requirements

Require **poppler-utils** package for pdf2image python module

## Run

You can run the script with this command :

```shell
python3 src/parser.py
```

## Arguments and variables

Argument | Environnement variable | json parameter | Comment | Default value
---------|----------|---------|--------- | ---------
 `-w <folder>`, `--workdir <folder>` | `WORKDIR` | `workdir` | Temp folder used by the script | `None`
 `-o <folder>`, `--output <folder>` | `OUTPUT` | `output` |  Output folder where ics are generated | `None`
 `-c <folder>`, `--config <file>` | `CONFIG` | `config` | Config file is localisation | `config/config.json`
 `-d`, `--detect` | `DETECT` | `detect` | Save detected element of pdf in the temp folder | `false`
 `-p`, `--print` | `PRINT` | `print` | Print classes genarated in stdout | `false`
 `-t <seconds>`, `--time <seconds>` | `TIME` | `time` | Run this script in a loop for every TIME seconds | `None`
 `--force` | `FORCE` | `force` | Force pdf parsing even if it's the same than remote | `false`
 `-h`, `--help` | / | / | Show helper for this script | /
 `--version` | / | / | Show version of script | /

## Config and data files

### Config

[Here is](sample/config.json) a config sample :

_It should be in the config folder named `config.json`_

### FTP connexion

When one or more ftp connexions are provided, this script uses it and send the file in root folder

To do so you need to setup your FTP credentials by adding a "ftp" key in `config.json` file like this :

```json
{
    "ftp": [{
        "host":"your_host",
        "port":21,
        "user": "your_user",
        "password": "your_password",
        "ssl": true
    }]
}
```

## Container

### Build

There is a [Dockerfile](Dockerfile) build on top of `python:3.10-slim`

To build it run

```shell
docker build -t <tag> . 
```

### Volumes and variable

Variables is the same than variable section.

You have to set :

- a config volume mapped on `/config`
- a volume for ics output mapped on `/output` (optional)

### Deploy

You can use the [docker compose](docker-compose.yml) file to deploy it (volume map has to be changed)
