# pypi-mirror

Simple PyPI Mirror

```sh
$ ./pypi-mirror.py --help
Usage: pypi-mirror.py [options]

Options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory=DIRECTORY
                        path to py-packages
  -p PACKAGES, --packages=PACKAGES
                        packages list
  -l PIP_LOG, --pip-log=PIP_LOG
                        pip log
  -v, --verbose         verbose mode
```

## How-to use

```sh
$ pypi-mirror.py --directory=<directory> --packages=<file-with-packages>
```

After execution of this command in the directory will be created two sub-directories: packages/ and simple/. The packages/ directory will contain packages and simple/ directory will contain symlinks to packages for using with web server for local PyPI mirror.

The file with packages is simple text file where each python package is represented by one line

```
requests
lxml
scrapy
```

## How-to use with docker

```sh
$ docker build -t 'ownport/pypi-mirror:dev' .
Sending build context to Docker daemon 9.911 MB
Step 1 : FROM alpine:latest
 ---> 70c557e50ed6
Step 2 : RUN apk add --update python py-pip
 ---> Running in 534db45e2d3e
....
Successfully built 3d9f9aa91213
$
$ docker images 
REPOSITORY                  TAG                 IMAGE ID            CREATED             SIZE
ownport/pypi-mirror         dev                 fd4b31ee8b0d        28 minutes ago      51.92 MB
$
$ docker run -ti --rm --name pypi-mirror -v $(pwd)/pypi-mirror.py:/bin/pypi-mirror.py  ownport/pypi-mirror:dev /bin/sh
$
$ echo lxml > packages.req
$
$ ./bin/pypi-mirror.py --directory /tmp --packages packages.req
$
$ ls -l /tmp/packages/
total 3724
-rw-r--r--    1 root     root       3810202 Mar  8 15:05 lxml-3.5.0.tar.gz
$
$ ls -l /tmp/simple/lxml/
total 0
lrwxrwxrwx    1 root     root            32 Mar  8 15:05 lxml-3.5.0.tar.gz -> ../../packages/lxml-3.5.0.tar.gz
$
```

## Links

- [pip](https://pip.pypa.io/en/stable/)
- [wolever/pip2pi](https://github.com/wolever/pip2pi) builds a PyPI-compatible package repository from pip requirements


