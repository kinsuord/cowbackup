# Cowbackup

## description
Cowbackup is a backup tool using python.

## Usage
settting in .yaml file

``` yaml
filters:
  - name: force_backup
    include:
      - "*/backup/*"
  - name: document
    include:
      - "*.docx"
      - "*.doc"
      - "*.pdf"
      - "*.md"
  - name: zip_file
    include:
      - "*.zip"
      - "*.7z"
  - name: google
    include:
      - "*.gmap"
      - "*.gdoc"
  - name: unity_project
    include:
      - "*/Assets/*"
      - "*/Packages/*"
      - "*/ProjectSettings/*"
    exclude:
      - "*/[Ll]ibrary/*"
      - "*/[Tt]emp/*"
      - "*/[Oo]bj/*"
      - "*/[Bb]uild/*"
      - "*/[Bb]uilds/*"
      - "*/[Ll]ogs/*"
      - "*/[Mm]emoryCaptures/*"  

tasks:
  - name: project
    source: "D:/Liang/project"
    target: "E:/cowbackup/project"
    dont_delete: No
    filter:
      pre_defined:
        - document
        - zip_file
        - google
        - unity_project
      include:
        - "*.md"
        - "*/.git/*"
      exclude:
        - "*/readme.md"
```
About the rule of filter the files. Please see [fnmatch](https://docs.python.org/zh-tw/3/library/fnmatch.html)

## Run

See `run.bat`

``` bat
call D:\tool\anaconda\Scripts\activate.bat base
python cobackpy.py tasks.yaml
conda deactivate
```

> **Caution**: `dont_delete` will remove files from target folder when the files aren't in the source folder and vice versa.

> it's recommended to run `python cobackpy.py tasks.yaml --test` first.

In fact, following is the update/delete logic.

```python
# if source have but target don't have
if source_mtime > last_update_time:
    ops.append(Op('new', target, source))
elif not task['dont_delete']:
    ops.append(Op('delete', source))

# if target have but source don't have
if target_mtime > last_update_time:
    ops.append(Op('new', source, target))
elif not task['dont_delete']:
    ops.append(Op('delete', target))
```

## TODO

- [ ] using [win32](https://pypi.org/project/pywin32/) to automatically set up to task scheduler
- [ ] GUI
- [ ] Unexpect input handler