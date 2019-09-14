# Cobackpy

## description
Cobackpy is a backup tool using python.

## Usage
settting in setting.yaml

```yaml
start_folder:
 D:/
 
include:
 - ./class/**
 - ./old/**
 - ./portfolio/**
 - ./project/**

exclude:
 - "**/dataset/**"
 - "**/datasets/**"
 - "**/~*"
 - "**/checkpoint/**"
 - "**.pickle"
 - "**.pt"
 - "**/.*/**"
 - "**/node_modules/**"
 - "**/__pycache__/**"

target:
 E:/backup
```
About the rule of include and exclude files. Please see [fnmatch](https://docs.python.org/zh-tw/3/library/fnmatch.html)

And it will generate .log on same directory

## TODO

- [ ] using [win32](https://pypi.org/project/pywin32/) to automatically set up to task scheduler
- [ ] GUI
- [ ] walk file more efficiently [scandir](https://github.com/benhoyt/scandir)
- [ ] Do not walk file while directory in exclude list
