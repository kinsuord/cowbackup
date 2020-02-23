# Cowbackup

## description
Cowbackup is a backup tool using python.

## Usage
settting in .yaml file

```yaml
filters:
  - name: force_backup
    must_include:
      - "**/backup/**"
  - name: document
    include:
      - "**.docx"
      - "**.doc"
      - "**.pdf"
  - name: zip_file
    include:
      - "**.zip"
      - "**.7z"

tasks:

  - name: project
    source: "D:/project"
    target: "E:/cowbackup/project"
    filter:
      pre_defined:
        - document
        - zip_file
        - force_backup
      include:
        - "**.md"
        - "**/.git/**"
      exclude:
        - "**/readme.md"
```
About the rule of filter the files. Please see [fnmatch](https://docs.python.org/zh-tw/3/library/fnmatch.html)


## TODO

- [ ] using [win32](https://pypi.org/project/pywin32/) to automatically set up to task scheduler
- [ ] GUI
- [ ] Unexpect input handler
- [ ] Delete the folder when deleting the files
